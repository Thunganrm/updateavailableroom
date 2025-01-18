
import asyncio
import json
import requests
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import itertools
from flask import Flask, jsonify, send_file, render_template
import pandas as pd

app = Flask(__name__)

# Hàm cập nhật dữ liệu

hotel_responses=[]
async def update_data():
    global result_df
    async def main():
        global hotel_responses,result_df
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
  # Chế độ headless
            page = await browser.new_page()

            # Truy cập trang đăng nhập
            await page.goto("https://id.bluejaypms.com/login")
            await page.select_option("select[name='ddlLangCode']", "vi-VN")
            await page.fill("input[name='txtEmail']", "ngan.lalahouse@gmail.com")
            await page.fill("input[name='txtPassword']", "Hotelhelper@2024")
            await page.click("a#lkLogin")
            await page.wait_for_timeout(5000)

            # Lấy cookies sau khi đăng nhập
            await page.wait_for_selector("#lvHotels_lbtNameHotel_0")
            await page.click("#lvHotels_lbtNameHotel_0")
            await page.wait_for_timeout(5000)

            cookies = await page.context.cookies()
            print(cookies)

            keys_to_keep = [
                "ASP.NET_SessionId", "HtLanguage", "HtToken", "HtHotelId", "HtBaseDir"
            ]
            filtered_cookies = [cookie for cookie in cookies if cookie['name'] in keys_to_keep]

            # Thay đổi giá trị của HtHotelId
            new_ht_hotel_id_list = ["5998", "6001", "6062"]
            hotel_responses = []

            # Lặp qua danh sách khách sạn và gửi yêu cầu POST
            for new_ht_hotel_id in new_ht_hotel_id_list:
                for i, cookie in enumerate(filtered_cookies):
                    if cookie['name'] == 'HtHotelId':
                        filtered_cookies[i]['value'] = new_ht_hotel_id
                        break

                cookie_header = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in filtered_cookies])

                url = "https://id.bluejaypms.com/app/Room/GetRoomAvails"
                headers = {
                    "Accept": "*/*", "Accept-Encoding": "gzip, deflate, br, zstd", "Accept-Language": "en-US,en;q=0.9,vi;q=0.8",
                    "Content-Type": "application/json; charset=UTF-8", "Referer": "https://id.bluejaypms.com/app/calendar",
                    "Origin": "https://id.bluejaypms.com", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
                    "Cookie": cookie_header
                }

                data = [
                    {"Action": "UpdateAvail", "RoomTypeId": "9197", "FromDate": "2024-12-02", "ToDate": "2024-12-05"},
                    {"Action": "UpdateAvail", "RoomTypeId": "9198", "FromDate": "2024-12-02", "ToDate": "2024-12-05"},
                    {"Action": "UpdateAvail", "RoomTypeId": "9199", "FromDate": "2024-12-02", "ToDate": "2024-12-05"},
                    {"Action": "UpdateAvail", "RoomTypeId": "9207", "FromDate": "2024-12-02", "ToDate": "2024-12-05"},
                    {"Action": "UpdateAvail", "RoomTypeId": "9208", "FromDate": "2024-12-02", "ToDate": "2024-12-05"},
                    {"Action": "UpdateAvail", "RoomTypeId": "9206", "FromDate": "2024-12-02", "ToDate": "2024-12-05"},
                    {"Action": "UpdateAvail", "RoomTypeId": "9555", "FromDate": "2024-12-02", "ToDate": "2024-12-05"},
                    {"Action": "UpdateAvail", "RoomTypeId": "9556", "FromDate": "2024-12-02", "ToDate": "2024-12-05"},
                    {"Action": "UpdateAvail", "RoomTypeId": "9557", "FromDate": "2024-12-02", "ToDate": "2024-12-05"},
                    {"Action": "UpdateAvail", "RoomTypeId": "9558", "FromDate": "2024-12-02", "ToDate": "2024-12-05"},
                    {"Action": "UpdateAvail", "RoomTypeId": "9559", "FromDate": "2024-12-02", "ToDate": "2024-12-05"},
                ]

                json_data = json.dumps(data)
                response = requests.post(url, headers=headers, data=json_data)
                print(f"Response for hotel ID {new_ht_hotel_id}: {response.text}")

                if response.status_code == 200:
                    hotel = response.json()
                    hotel_responses.append(hotel)
                else:
                    print(f"Request failed for hotel ID {new_ht_hotel_id} with status code: {response.status_code}")

            await browser.close()

        # Xử lý dữ liệu và tạo DataFrame
        bt = list(itertools.chain.from_iterable(hotel_responses))

        rooms_data = [
            {"RoomType_Id": "9206", "room_name": "Deluxe Double Room"},
            {"RoomType_Id": "9207", "room_name": "King room with garden view"},
            {"RoomType_Id": "9208", "room_name": "King room with Balcony"},
            {"RoomType_Id": "9197", "room_name": "Deluxe Double Room"},
            {"RoomType_Id": "9198", "room_name": "King room with garden view"},
            {"RoomType_Id": "9199", "room_name": "King room with Balcony"},
            {"RoomType_Id": "9555", "room_name": "Superior"},
            {"RoomType_Id": "9556", "room_name": "Deluxe"},
            {"RoomType_Id": "9557", "room_name": "Luxury"},
            {"RoomType_Id": "9558", "room_name": "Queen"},
            {"RoomType_Id": "9559", "room_name": "Standard"},
        ]

        rooms_df = pd.DataFrame(rooms_data)
        hotels_data = [
            {"HotelId": "6001", "hotel_name": "Ben Thanh Inn"},
            {"HotelId": "5998", "hotel_name": "Elegant Feel Inn"},
            {"HotelId": "6062", "hotel_name": "MG Daisy"},
        ]
        hotels_df = pd.DataFrame(hotels_data)

        df = pd.DataFrame(bt)
        print(df)

        df['SellFrom'] = df['SellFrom'].apply(lambda x: datetime.strptime(x.replace('T', ' ').split('.')[0], '%Y-%m-%d %H:%M:%S'))
        df['SellTo'] = df['SellTo'].apply(lambda x: datetime.strptime(x.replace('T', ' ').split('.')[0], '%Y-%m-%d %H:%M:%S'))

        start_date = datetime.today()
        end_date = start_date + timedelta(days=6)
        date_range = pd.date_range(start=start_date, end=end_date).strftime('%Y-%m-%d').tolist()

        result = []
        for room_type in df['RoomType_Id'].unique():
            room_data = df[df['RoomType_Id'] == room_type]
            hotel_id = df[df['RoomType_Id'] == room_type]['HotelId'].values[0]
            room_availability = {"RoomType_Id": room_type, 'HotelId': hotel_id}

            for date in date_range:
                total_value = 0
                for _, row in room_data.iterrows():
                    sell_from = row['SellFrom']
                    sell_to = row['SellTo']
                    value = row['Value']
                    if sell_from <= datetime.strptime(date, '%Y-%m-%d') <= sell_to:
                        total_value += value
                room_availability[date] = total_value

            result.append(room_availability)

        final_df = pd.DataFrame(result)
        final_df['RoomType_Id'] = final_df['RoomType_Id'].astype(str)
        rooms_df['RoomType_Id'] = rooms_df['RoomType_Id'].astype(str)
        hotels_df['HotelId'] = hotels_df['HotelId'].astype(str)
        final_df['HotelId'] = final_df['HotelId'].astype(str)

        result_df = final_df.merge(rooms_df, on='RoomType_Id', how='left')
        result_df = result_df.merge(hotels_df, on='HotelId', how='left')
        result_df = result_df.drop(columns=['RoomType_Id', 'HotelId'], axis=1)
        result_df = result_df[['hotel_name', 'room_name'] + [col for col in result_df.columns if col not in ['hotel_name', 'room_name']]]
        return result_df

    await main()

result_df=0
@app.route("/", methods=["GET"])
def run_update_data():
    global result_df
    asyncio.run(update_data())  # Cập nhật dữ liệu
    print('update')
    resultList = {col: result_df[col].to_list() for col in result_df.columns}
    # resultList={'2025-01-17': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '2025-01-18': [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], '2025-01-19': [0, 1, 0, 3, 0, 0, 0, 0, 0, 0, 0], '2025-01-20': [1, 0, 1, 1, 0, 3, 0, 1, 1, 0, 0], '2025-01-21': [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], '2025-01-22': [1, 0, 0, 1, 1, 4, 0, 0, 0, 0, 1], '2025-01-23': [0, 0, 1, 0, 1, 0, 0, 1, 0, 0, 0], '2025-01-24': [1, 0, 0, 0, 1, 3, 1, 1, 0, 0, 0], '2025-01-25': [1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 1], '2025-01-26': [0, 0, 1, 0, 0, 0, 2, 0, 0, 1, 0], '2025-01-27': [0, 1, 2, 1, 0, 2, 1, 0, 0, 0, 0], '2025-01-28': [0, 0, 0, 0, 0, 0, 0, 1, 1, 0, 1], '2025-01-29': [0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0], '2025-01-30': [0, 0, 0, 0, 0, 0, 1, 1, 0, 0, 0], '2025-01-31': [0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0], '2025-02-01': [0, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1], 'room_name': ['Luxury', 'King room with Balcony', 'Superior', 'Deluxe Double Room', 'Queen', 'Deluxe Double Room', 'King room with garden view', 'Deluxe', 'Standard', 'King room with Balcony', 'King room with garden view'], 'hotel_name': ['MG Daisy', 'Elegant Feel Inn', 'MG Daisy', 'Elegant Feel Inn', 'MG Daisy', 'Ben Thanh Inn', 'Elegant Feel Inn', 'MG Daisy', 'MG Daisy', 'Ben Thanh Inn', 'Ben Thanh Inn']}
    return render_template('index.html', resultList=resultList)
if __name__ == "__main__":
  # Nếu không có PORT thì dùng cổng mặc định 5000

    app.run(host='0.0.0.0', port=5000)
