import pandas as pd
import requests
import json

# Set up authentication
OUTPUT_FOLDER = "/home/hautp2/Desktop/ai-mps-studio/services/web/project/testcase-output/tc_output_hautp2.xlsx"
OUTPUT_CONVERTED_FOLDER = "/home/hautp2/Desktop/ai-mps-studio/services/web/project/testcase-output/tc_output_converted_hautp2.xlsx"


def read_workbook(user_id):
    print("Starting to read file excel")
    # Read file excel
    df = pd.read_excel(OUTPUT_FOLDER)
    # Set display options to show merged cells
    pd.set_option('display.expand_frame_repr', False)
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    col1 = df['Testcase description']
    col2 = df['Test to perform']

    # List the required formats
    count = 0
    na_arr = []
    for i in range(len(col1)):
        if pd.isnull(col1[i]) is False:
            na_arr += [i]
            count += 1

    print(na_arr)
    # Create an objects Series from na_arr
    na_series = pd.Series(na_arr)
    count = 0
    na_series_i = 0
    start_na_series = 0
    msg = ""
    test_perform_arr = []
    # Export message file
    for c_desc_i in range(len(col1)):
        if pd.isnull(col1[c_desc_i]) is False:
            count += 1
            for na_series_i in range(start_na_series, len(na_series)):
                try:
                    # print(f"{na_arr[na_series_i]} >> {na_arr[na_series_i + 1]}")
                    for k in range(na_arr[na_series_i], na_arr[na_series_i + 1]):
                        if pd.isnull(col2[k]) is False:
                            test_perform_arr += [col2[k]]

                    start_na_series += 1
                except BaseException:
                    try:
                        for j in range(max(na_arr), max(na_arr) * 10):
                            if pd.isnull(col2[j]) is False:
                                test_perform_arr += [col2[j]]

                    except BaseException:
                        print("")

                output = ""
                for i, step in enumerate(test_perform_arr):
                    output += f"{step}\n"

                # print(output)

                # Define a prompt for the chatbot
                url = "https://api.openai.com/v1/chat/completions"

                payload = json.dumps({
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {
                            "role": "user",
                            "content": f"Hãy bổ sung Test to perform cho Testcase description: {col1[c_desc_i]} chatgpt phản hồi bằng tiếng việt: " + output
                        }
                    ],
                    "temperature": 0.7
                })
                headers = {
                    'Content-Type': 'application/json',
                    'Authorization': 'Bearer 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'
                }

                response = requests.request("POST", url, headers=headers, data=payload)

                data = json.loads(response.text)

                # truy cập vào value của content
                content = data["choices"][0]["message"]["content"]

                test_desc = col1[c_desc_i]
                test_steps = [content]

                print(f"*************{col1[c_desc_i]}*********************")
                print(test_steps)
                test_steps_str = "\n".join(test_steps)
                df = pd.DataFrame({'Testcase description': [test_desc], 'Test to perform': [test_steps_str]})
                df = df.assign(**{'Test to perform': df['Test to perform'].str.split('\n')}).explode('Test to perform')

                # save to Excel
                # Lưu DataFrame vào file Excel đã tồn tại
                with pd.ExcelWriter(OUTPUT_CONVERTED_FOLDER, mode='a', engine='openpyxl') as writer:
                    df.to_excel(writer, sheet_name='Sheet', index=False, header=False, if_sheet_exists='replace')

                break


read_workbook("user_id")


