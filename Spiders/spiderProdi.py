import scrapy
import os
import pandas as pd


def labelConcate(a, b):
    return '{}_{}'.format(a, b)


def replaceStrByIndex(string, i, newLetter):
    return "".join((string[:i], newLetter, string[i + 1:]))


class spiderProdi(scrapy.Spider):
    df = pd.read_csv("dataPTN.csv")
    ptnData = df['kode_ptn'].astype(str)

    name = 'spiderProdi'
    allowed_domains = ['sbmptn.ltmpt.ac.id']

    start_urls = ['https://sbmptn.ltmpt.ac.id/index.php?mid=14&ptn={ptn}&jenis=`'.format(
        ptn=ptn) for ptn in ptnData]

    base_url = 'https://sbmptn.ltmpt.ac.id/'

    fileFormat = 'csv'
    fileName = 'dataProdi' + '.' + fileFormat
    fileAvailable = os.path.isfile(fileName)

    if fileAvailable:
        open(fileName, 'w+')

    custom_settings = {
        'FEED_FORMAT': fileFormat,
        'FEED_URI': fileName
    }

    def parse(self, response):
        MAIN_XPATH = '/html/body/div[2]/div/div[2]/div/div[1]/div/div[2]/div[2]'

        TABLE_XPATH = MAIN_XPATH + \
            '/div/div[position()>0 and position()<=last()]/table[1]/tbody'
        TABLE_SELECTOR = response.xpath(TABLE_XPATH)

        RECORD_XPATH = './/tr[position()>0 and position()<=last()]'
        RECORD_SELECTOR = TABLE_SELECTOR.xpath(RECORD_XPATH)

        for rset in RECORD_SELECTOR:
            DATA = {}

            sebaran_link = rset.xpath('.//td[6]/a/@href').extract_first()

            sebaran_url = self.base_url + sebaran_link

            DATA['kode_prodi'] = rset.xpath(
                './/td[1]/text()').extract_first(),
            DATA['nama_prodi'] = rset.xpath(
                './/td[2]/text()').extract_first(),
            DATA['rumpun'] = sebaran_link[-1],
            DATA['daya_tampung_2019'] = rset.xpath(
                './/td[3]/text()').extract_first(),
            # DATA['peminat_2018'] = rset.xpath('.//td[4]/text()').extract_first(),

            yield scrapy.Request(
                response.urljoin(sebaran_url),
                callback=self.parse_sebaran,
                meta={'data': DATA}
            )

    def parse_sebaran(self, response):

        DATA = response.meta['data']

        SUB_XPATH = '/html/body/div[2]/div/div[2]/div/div[2]/div[2]/div[2]'

        SUB_TABLE_XPATH = SUB_XPATH + '/table[1]'
        SUB_TABLE_SELECTOR = response.xpath(SUB_TABLE_XPATH)

        SUB_RECORD_XPATH = SUB_TABLE_XPATH + \
            '/tbody/.//tr[position()>0 and position()<=last()]'
        SUB_RECORD_SELECTOR = SUB_TABLE_SELECTOR.xpath(SUB_RECORD_XPATH)

        SUB_LABEL_XPATH = SUB_TABLE_XPATH + \
            '/thead/.//tr[position()>0 and position()<=last()]'
        SUB_LABEL_SELECTOR = SUB_TABLE_SELECTOR.xpath(SUB_LABEL_XPATH)

        SUB_LABEL = {}

        for sub_lset in SUB_LABEL_SELECTOR:
            SUB_LABEL[0] = sub_lset.xpath(
                './/th[2]/text()').extract_first()  # 2016
            SUB_LABEL[1] = sub_lset.xpath(
                './/th[3]/text()').extract_first()  # 2017
            SUB_LABEL[2] = sub_lset.xpath(
                './/th[4]/text()').extract_first()  # 2018

        for sub_rset in SUB_RECORD_SELECTOR:
            LABEL_SEBARAN = sub_rset.xpath(
                './/td[1]/text()').extract_first()

            if LABEL_SEBARAN is None:
                continue

            LABEL_SEBARAN = LABEL_SEBARAN.replace(" ", "_").lower()

            DATA[labelConcate(LABEL_SEBARAN, SUB_LABEL[2])] = sub_rset.xpath(
                './/td[4]/text()').extract_first()
            DATA[labelConcate(LABEL_SEBARAN, SUB_LABEL[1])] = sub_rset.xpath(
                './/td[3]/text()').extract_first()
            DATA[labelConcate(LABEL_SEBARAN, SUB_LABEL[0])] = sub_rset.xpath(
                './/td[2]/text()').extract_first()

        yield DATA
