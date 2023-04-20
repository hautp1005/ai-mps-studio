import openai
import pandas as pd

# Set up authentication
# openai.api_key = "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"
OUTPUT_FOLDER = "/home/hautp2/Desktop/ai-mps-studio/services/web/project/testcase-output/tc_output_hautp2.xlsx"


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
                    output += f"{step};"

                # print(output)

                # Define a prompt for the chatbot
                prompt = "Hãy bổ sung Test to perform cho Testcase description: " + col1[c_desc_i] \
                         + ". Nội dung như sau : " \
                         + output
                print(prompt.strip())

                break


read_workbook("user_id")
