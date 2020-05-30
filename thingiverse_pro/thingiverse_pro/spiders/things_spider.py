import scrapy
from scrapy.loader import ItemLoader
import sys
from ..items import MainItemLoader, CommLoader
from ..items import ThingiverseProItem
from math import ceil


class ThingsSpider(scrapy.Spider):
    name = "things"

    def stripping(self, list_unstriped):
        for x in list_unstriped:
            yield x.strip()

    def start_requests(self):
        with open("last_nb/num_thing.txt", "r") as f:
            max_thing = int(f.read())

        urls = []
        for i in list(range(1, max_thing + 1))[::-1]:
            urls.append(f"https://www.thingiverse.com/thing:{i}")
        for url in urls:
            yield scrapy.Request(url=url,                                
                                 meta={'num_thing': url.rsplit(':', 1)[-1]},
                                 callback=self.parse_main)

    def parse_main(self, response):
        ldr = MainItemLoader(item=ThingiverseProItem(), response=response)
        num_thing = response.xpath("//*[@class='top_content item-list-interactions']/@data-thing-id").get()
        ldr.add_value('num_thing', num_thing)
        ldr.add_value('title',
                      response.css('#main > div > div.item-page-header > div > h1::text').extract_first().strip())
        ldr.add_css('author', '#main > div > div.item-page-header > div > span:nth-child(2) > a::text', self.stripping)

        tags = ldr.nested_xpath("//*[@class='taglist']/a")
        if ldr.get_xpath("//*[@class='taglist']/a"):
            tags.add_xpath('tags', 'text()')
        else:
            tags.add_value('tags', 'None')

        if ldr.get_xpath("//*[@class='thing-info-content rendered-markdown']/h1"):
            ldr.add_xpath('desc_title', "//*[@class='thing-info-content rendered-markdown']/h1/text()", self.stripping)
        else:
            ldr.add_value('desc_title', 'None')

        if ldr.load_item()['desc_title'] == ['None']:
            ldr.add_value('desc_cont', 'None')
        else:
            for i in ldr.load_item()['desc_title']:
                str_desc_title = f"//*[@class='thing-info-content rendered-markdown']" \
                                 f"//text()[not(ancestor::h1)][preceding::h1[1][text()='{i}']]"
                str_desc_cont = response.xpath(str_desc_title).extract()
                for idx, val in enumerate(str_desc_cont):
                    str_desc_cont[idx] = val.strip()
                ldr.add_value('desc_cont', '\n'.join(str_desc_cont))

        ldr.add_css('date_thing', "#main > div > div.item-page-header > div > span:nth-child(3)::text", self.stripping)
        ldr.add_xpath('like', "//a[@title='Like']/span/text()")
        ldr.add_xpath('license', "//*[@class='small-text']/div[@class='thing-license']/@title")

        views = response.xpath("//div[@class='icon-views stats-item img-btn']/text()").extract()[0].strip().split()[0]
        ldr.add_value('views', views)

        downld = response.xpath("//div[@class='icon-download-dark stats-item img-btn']/text()").extract()[0].split()[0]
        ldr.add_value('downloads', downld)

        num_remixes = int(response.xpath("//div[@class='block_nav bottom_content']/a[7]/@data-count").extract_first())
        num_makes = int(response.xpath("//div[@class='block_nav bottom_content']/a[5]/@data-count").extract_first())

        last_page_remix = ceil(num_remixes/24)
        if last_page_remix == 0:
            last_page_remix = 1

        last_page_make = ceil(num_makes/24)
        if last_page_make == 0:
            last_page_make = 1

        print(sys.version)
        with open(f"/html/things/{num_thing}.html", "wb") as f:
            f.write(response.text.encode('utf8'))

        yield scrapy.Request(url='https://www.thingiverse.com/thing:' + response.meta['num_thing'] + '/comments',
                              
                              meta={'num_thing': response.meta['num_thing'],
                                    'num_remixes': num_remixes,
                                    'num_makes': num_makes,
                                    'last_page_remix': last_page_remix,
                                    'last_page_make': last_page_make,
                                    'item': ldr},
                              callback=self.parse_comments)
        return

    def parse_comments(self, response):
        ldr = response.meta['item']

        ldr.add_value('comm', self.get_comm(response))

        with open(f"/html/comments/{response.meta['num_thing']}.html", "wb") as f:
            f.write(response.text.encode('utf8'))

        if response.meta['num_remixes'] == 0:
            ldr.add_value('remixes', 'None')
            if response.meta['num_makes'] == 0:
                ldr.add_value('makes', 'None')
                with open('last_nb/num_thing.txt', 'w') as f:
                    f.write(response.meta['num_thing'])
                yield ldr.load_item()
                return
            else:
                yield scrapy.FormRequest(url='https://www.thingiverse.com/thing:' + response.meta['num_thing'] + '/makes',
                                          
                                          meta={'item': ldr,
                                                'num_thing': response.meta['num_thing'],
                                                'num_makes': response.meta['num_makes'],
                                                'last_page_make': response.meta['last_page_make']},
                                          callback=self.parse_makes_1)
                return
        else:
            yield scrapy.Request(url='https://www.thingiverse.com/thing:' + response.meta['num_thing'] + '/remixes',
                                  
                                  meta={'num_thing': response.meta['num_thing'],
                                        'num_remixes': response.meta['num_remixes'],
                                        'num_makes': response.meta['num_makes'],
                                        'last_page_remix': response.meta['last_page_remix'],
                                        'last_page_make': response.meta['last_page_make'],
                                        'item': ldr},
                                  callback=self.parse_remixes_1)
            return

    def get_comm(self, response):
        comm_ld = CommLoader(response=response)

        if comm_ld.get_xpath('//*[@class="comment-container\n     "]/@id'):
            comm_ld.add_xpath('id_container', '//*[@class="comment-container\n     "]/@id')
        if comm_ld.get_xpath("//*[@class='comment-container\n      comment-maker']/@id"):
            comm_ld.add_xpath('id_container', "//*[@class='comment-container\n      comment-maker']/@id")

        comm_ld_item = comm_ld.load_item()
        if 'id_container' in comm_ld_item:
            for key, value in comm_ld_item.items():
                for i in value:
                    str_comm_date = f"#{i}-wrapper > div > div.comment-header > div > div > a > span::text"
                    if comm_ld.get_css(str_comm_date):
                        comm_ld.add_value('comm_date', response.css(str_comm_date).extract_first().strip())
                    else:
                        comm_ld.add_value('comm_date', 'None')

                    str_comm_author = f"#{i}-wrapper > div > div.comment-header > div > a::text"
                    if comm_ld.get_css(str_comm_author):
                        comm_ld.add_value('comm_author', response.css(str_comm_author).extract_first().strip())
                    else:
                        comm_ld.add_value('comm_author', 'None')

                    str_comm_content = f"//*[@id='{i}-wrapper']/div/span/div/div/*//text()"
                    str_del_comm = f"#{i} > div.comment-body.content-box.full-width.deleted-comment"
                    if comm_ld.get_xpath(str_comm_content):
                        comm_ld.add_value('comm_content', '\n'.join(response.xpath(str_comm_content).extract()))
                    else:
                        if comm_ld.get_css(str_del_comm):
                            comm_ld.add_value('comm_content', 'Comments deleted.')
                        else:
                            comm_ld.add_value('comm_content', 'None')

                    str_papa_id = f"//*[@id='{i}-wrapper']/parent::div/parent::div/parent::div/@id"
                    if (comm_ld.get_xpath(str_papa_id)) and \
                            (response.xpath(str_papa_id).extract_first() != 'thing-comments'):
                        comm_ld.add_xpath('papa_id', str_papa_id)
                    else:
                        comm_ld.add_value('papa_id', 'None')
        else:
            comm_ld.add_value('id_container', 'None')
            comm_ld.add_value('comm_content', 'None')
            comm_ld.add_value('papa_id', 'None')
            comm_ld.add_value('comm_author', 'None')
            comm_ld.add_value('comm_date', 'None')
        yield comm_ld.load_item()
        return

    def parse_remixes_1(self, response):
        ldr = response.meta['item']
        with open(f"/html/remixes/{response.meta['num_thing']}_1.html", "wb") as f:
            f.write(response.text.encode('utf8'))

        ldr.add_value('remixes', set(response.xpath("//*[@class='thing item thing-card ']/@data-id").getall()))
        if response.meta['num_makes']:        
            yield scrapy.Request(url='https://www.thingiverse.com/thing:' + response.meta['num_thing'] + '/makes',
                                 
                                 meta={'item': ldr,
                                       'num_thing': response.meta['num_thing'],
                                       'num_makes': response.meta['num_makes'],
                                       'last_page_make': response.meta['last_page_make']},
                                 callback=self.parse_makes_1)
            return
        else:
            ldr.add_value('makes', 'None')
            with open('last_nb/num_thing.txt', 'w') as f:
                 f.write(response.meta['num_thing'])
            yield ldr.load_item()
            return
        if response.meta['last_page_remix'] > 1:
            yield scrapy.FormRequest(url='https://www.thingiverse.com/ajax/things/remixes',
                                      
                                      method="POST",
                                      formdata={'page': '2', 'id': response.meta['num_thing']},
                                      headers={'x-requested-with': 'XMLHttpRequest',
                                               'content-type': ['application/x-www-form-urlencoded','charset=UTF-8']},
                                      meta={'page': 2, 'item': ldr,
                                            'num_thing': response.meta['num_thing'],
                                            'num_makes': response.meta['num_makes'],
                                            'last_page_remix': response.meta['last_page_remix'],
                                            'last_page_make': response.meta['last_page_make']},
                                      callback=self.parse_remixes)
            return


    def parse_remixes(self, response):
        ldr = response.meta['item']

        with open(f"/html/remixes/{response.meta['num_thing']}_{response.meta['page']}.html", "wb") as f:
            f.write(response.text.encode('utf8'))

        page = response.meta.get('page')
        ldr.add_value('remixes',
                      set(response.xpath("//*[@class='thing item thing-card 'and @data-type='things']/@data-id").getall()))

        if str(page) == str(response.meta['last_page_remix']):
            if response.meta['num_makes']:
                yield scrapy.Request(url='https://www.thingiverse.com/thing:' + response.meta['num_thing'] + '/makes',
                                     
                                     meta={'item': ldr,
                                           'num_thing': response.meta['num_thing'],
                                           'num_makes': response.meta['num_makes'],
                                           'last_page_make': response.meta['last_page_make']},
                                     callback=self.parse_makes_1)
                return
            else:
                ldr.add_value('makes', 'None')
                with open('last_nb/num_thing.txt', 'w') as f:
                    f.write(response.meta['num_thing'])
                yield ldr.load_item()
                return
        page = int(page) + 1
        yield scrapy.FormRequest(url='https://www.thingiverse.com/ajax/things/remixes',
                                 
                                 method='POST',
                                 formdata={'page': str(page), 'id': response.meta['num_thing']},
                                 headers={'x-requested-with': 'XMLHttpRequest',
                                          'content-type': ['application/x-www-form-urldecoded', 'charset=UTF-8']},
                                 meta={'page': page,
                                       'item': ldr,
                                       'num_thing': response.meta['num_thing'],
                                       'last_page_remix': response.meta['last_page_remix'],
                                       'last_page_make': response.meta['last_page_make'],
                                       'num_makes': response.meta['num_makes']},
                                 callback=self.parse_remixes)

    def parse_makes_1(self, response):
        ldr = response.meta['item']

        with open(f"/html/makes/{response.meta['num_thing']}_1.html", "wb") as f:
            f.write(response.text.encode('utf8'))

        ldr.add_value('makes', set(response.xpath("//div[@class='make item make-card ']/@data-id").getall()))

        if response.meta['num_makes'] <= 24:
            with open('last_nb/num_thing.txt', 'w') as f:
                f.write(response.meta['num_thing'])
            yield ldr.load_item()
            return

        if response.meta['last_page_make'] > 1:
            yield scrapy.FormRequest(url='https://www.thingiverse.com/ajax/things/makes',
                                    
                                      method="POST",
                                      formdata={'page': '2', 'id': response.meta['num_thing']},
                                      headers={'x-requested-with': 'XMLHttpRequest',
                                               'content-type': ['application/x-www-form-urldecoded',
                                                                'charset=UTF-8']},
                                      meta={'page': 2, 'item': ldr,
                                            'num_thing': response.meta['num_thing'],
                                            'num_makes': response.meta['num_makes'],
                                            'last_page_make': response.meta['last_page_make']},
                                      callback=self.parse_makes)
            return

    def parse_makes(self, response):
        ldr = response.meta['item']
        page = response.meta.get('page')
        with open(f"/html/makes/{response.meta['num_thing']}_{response.meta['page']}.html", "wb") as f:
            f.write(response.text.encode('utf8'))

        ldr.add_value('makes',
                      set(response.xpath("//div[@class='make item make-card ' and @data-type='makes']/@data-id").getall()))
        if str(page) == str(response.meta['last_page_make']):
            with open('last_nb/num_thing.txt', 'w') as f:
                f.write(response.meta['num_thing'])
            yield ldr.load_item()
            return

        page = int(page) + 1
        yield scrapy.FormRequest(url='https://www.thingiverse.com/ajax/things/makes',
                                
                                 method='POST',
                                 formdata={'page': str(page), 'id': response.meta['num_thing']},
                                 headers={'x-requested-with': 'XMLHttpRequest',
                                          'content-type': ['application/x-www-form-urlencoded', 'charset=UTF-8']},
                                 meta={'page': page,
                                       'item': ldr,
                                       'num_thing': response.meta['num_thing'],
                                       'last_page_make': response.meta['last_page_make']},
                                 callback=self.parse_makes)

