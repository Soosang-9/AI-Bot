import urllib3
import xmltodict
import requests
from bs4 import BeautifulSoup as bs


class weather_parsing:
    def __init__(self):
        # input url with location
        self.URL_KOREA = 'http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=108'
        self.URL_BUSAN = 'http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=159'
        self.URL_SEOUL = 'http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=109'
        self.URL_JEONBUK = 'http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=146'
        self.URL_JEONNAM = 'http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=156'
        self.URL_GANGWON = 'http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=105'
        self.URL_CHUNGBUK = 'http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=131'
        self.URL_CHUNGNAM = 'http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=133'
        self.URL_KYUNGBUK = 'http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=143'
        self.URL_KYUNGNAM = 'http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=159'
        self.URL_JEJU = 'http://www.kma.go.kr/weather/forecast/mid-term-rss3.jsp?stnId=184'
        self.current_weather = {}
        self.current_weather_keys = []

        # city 정보넘겨줄때 in 으로 스플릿하기 때문에 부득이하게 인천은 yncheon으로표기.....
        self.city_info = {'seoul': '서울', 'jeju': '제주', 'busan': '부산', 'yncheon': '인천',
                          'daejeon': '대전', 'gwangju': '광주', 'daegu': '대구', 'ulsan': '울산'}

        self.current_weather_crol()
        self.get_current_weather_keys()

    # locate : city, Province -> by english
    # seoul, busan, daegu, yncheon, ulsan, daejeon, gwangju, gyeonggi, south_jeolla, north_jeolla
    # south&north_gyeongsang, south&north_chungcheong, gangwon
    # else -> korea forecast
    def get_weather_forecast(self, locate):
        result_txt = ""
        print(locate)
        if locate in self.city_info.keys():
            result_txt = self.get_current_weather_by_city(self.city_info[locate]) + " "
        http = urllib3.PoolManager()
        if locate in ('seoul', 'gyeonggi', 'yncheon'):
            r = http.request('get', self.URL_SEOUL)
        elif locate is 'gangwon':
            r = http.request('get', self.URL_GANGWON)
        elif locate is 'jeju':
            r = http.request('get', self.URL_JEJU)
        elif locate is 'north_chungcheong':
            r = http.request('get', self.URL_CHUNGBUK)
        elif locate is 'north_jeolla':
            r = http.request('get', self.URL_JEONBUK)
        elif locate in ('south_chungcheong', 'daejeon'):
            r = http.request('get', self.URL_CHUNGNAM)
        elif locate in ('south_jeolla', 'gwangju'):
            r = http.request('get', self.URL_JEONNAM)
        elif locate in ('south_gyeongsang', 'busan', 'ulsan'):
            r = http.request('get', self.URL_KYUNGNAM)
        elif locate in ('north_gyeongsang', 'daegu'):
            r = http.request('get', self.URL_KYUNGBUK)
        else:
            r = http.request('get', self.URL_KOREA)

        r2 = r.data.decode('utf-8', 'ignore').encode('utf-8')
        r3 = xmltodict.parse(r2)['rss']['channel']['item']['description']['header']['wf']
        r4 = str(r3).split('<br />')
        # print(r4)

        # for text in r4:
        #     result_txt += text
        # print(result_txt)
        result_txt += r4[0] + "" + r4[1]
        return result_txt

    # web crolling by city
    # key -> city name by korean
    # 날씨 : weather
    # 온도 : temp
    # 습도 : humid
    # 강수량 : precipitation
    # 풍향 : wind_to
    # 풍속 : wind_power
    def current_weather_crol(self):
        # 현재날씨 정보를 기상청 사이트에서 가져옴
        r = requests.get('http://www.kma.go.kr/weather/observation/currentweather.jsp')
        soup = bs(r.content, 'lxml')
        soup_table_body = soup.select('table > tbody > tr')
        for body in soup_table_body:
            locate = body.select('a')
            if len(locate) > 0:
                body_td = body.select('td')
                try:
                    precipi = float(body_td[8].text)
                except ValueError:
                    precipi = 0.0

                weather = str(body_td[1].text)
                if len(weather) < 1:
                    weather = "맑음"

                # 1: 현재일기(날씨) 2: 시정(km) 3: 운량 1/10 4: 중하운량 5: 현재기온
                # 6: 이슬점온도 7: 체감온도 8: 일강수(mm) 9: 습도(%) 10: 풍향 11: 풍속(m/s) 12: 해면기압
                # dictionary 에 key->도시이름 value에 원하는 정보 추가
                self.current_weather[locate[0].text] = {'weather': weather,                 # 날씨
                                                        'temp': body_td[5].text,            # 온도
                                                        'humid': body_td[9].text,           # 습도
                                                        'precipitation': precipi,           # 강수량
                                                        'wind_to': body_td[10].text,        # 풍향
                                                        'wind_power': body_td[11].text}     # 풍속
        return self.current_weather

    # 현재 날씨정보를 가져온 Dictionary 의 키값을 current_weather_keys 배열에 저장하여 return함
    def get_current_weather_keys(self):
        for key in self.current_weather.keys():
            self.current_weather_keys.append(key)

        return self.current_weather_keys

    # 해당하는 도시의 현재 날씨정보를 리턴함.
    # 강수량, 풍향, 풍속추가 가능.
    def get_current_weather_by_city(self, city):
        print(city)
        print(self.current_weather[city])
        if city not in self.current_weather_keys:
            print('wrong city.')
            return

        return_str = city+"의 현재 날씨는 " + self.current_weather[city]['weather'] + "입니다."
        return_str += " 기온은 " + self.current_weather[city]['temp'] + "도 이고,"
        return_str += " 습도는 " + self.current_weather[city]['humid'] + "입니다."

        return return_str


# 사용방법
# wp = weather_parsing()
# wp.current_weather_crol()
# seoul, busan, daegu, incheon, ulsan, daejeon, gwangju, gyeonggi, south_jeolla, north_jeolla
# south&north_gyeongsang, south&north_chungcheong, gangwon
# else -> korea forecast
# seoul 부분에위에있는도시목록중하나를넣으면결과값을텍스트로리턴한다잉
# text = wp.get_weather_forecast('seoul')
# print(text)

# 이외의도시(시&군 등)의기상정보는밑의키목록을확인하고호출
# 키확인
# keys = wp.get_current_weather_keys()
# print(keys)

# 위에서확인한키(도시)를입력하여날씨정보를받아옴(온도, 습도, 강수량, 풍향, 풍속)
# current_weather = wp.get_current_weather_by_city('서울')
# print(current_weather)

