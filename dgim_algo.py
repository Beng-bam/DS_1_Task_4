# Stream-mining: One hot encoding and DGIM Algo

from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder
import pandas as pd
import math
import streamlit as st

def one_hot_encoding(my_column):
    label = LabelEncoder()
    int_data = label.fit_transform(my_column)
    int_data = int_data.reshape(len(int_data), 1)
    print(list(label.classes_))
    print(int_data)

    onehot_data = OneHotEncoder(sparse=False)
    onehot_data = onehot_data.fit_transform(int_data)
    print("Categorical data encoded into integer values....\n")
    print("onehot_encoding", onehot_data)
    print(onehot_data)
    onehot_columns = list(zip(*onehot_data))
    return (onehot_data, onehot_columns, list(label.classes_))


def UpdateContainer(inputdict, klist, numkeys):
    for key in klist:
        if len(inputdict[key]) > 2:
            inputdict[key].pop(0)
            tstamp = inputdict[key].pop(0)
            if key != klist[-1]:
                inputdict[key * 2].append(tstamp)
        else:
            break


def OutputResult(inputdict, klist, wsize):
    cnt = 0
    firststamp = 0
    for key in klist:
        if len(inputdict[key]) > 0:
            firststamp = inputdict[key][0]
        for tstamp in inputdict[key]:
            print("size of bucket: %d, timestamp: %d" % (key, tstamp))
    for key in klist:
        for tstamp in inputdict[key]:
            if tstamp != firststamp:
                cnt += key
            else:
                cnt += 0.5 * key
    print("Estimated number of ones in the last %d bits: %d" % (wsize, cnt))
    return cnt

# Web Front-end

# title of the app:
st.title("Data Analysis with DGIM-Algorithm")

# Add a sidebar
st.sidebar.subheader("Settings")

# Setup file upload:
uploaded_file = st.sidebar.file_uploader(label="Upload your .csv file.", type='csv')

global df
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
char_columns = []

subheader_2 = st.subheader("Data Visualisation")

try:
    st.write(df)
    char_columns = list(df.columns)
except Exception as e:
    st.write("Please upload a file to the application.")


# adjusting the sidebar
# One hot encoding
column_sel = st.sidebar.selectbox(label='Choose a column for DGIM analysis:', options=char_columns)
chosen_column_main = df[column_sel]
possible_streams = one_hot_encoding(chosen_column_main)
choosing_binary_column = []
for k in range(len(possible_streams[1])):
    choosing_binary_column.append((k, possible_streams[2][k]))

choose_stream_1 = st.sidebar.selectbox(label='Choose a binary stream (column from one-hot encoding)',
                                     options=choosing_binary_column)
choose_stream = choose_stream_1[0]
window_length = st.sidebar.select_slider(label="Select the window length N", options=range(2048, 10240))
subheader = st.subheader("One-Hot Encoding")
try:
    st.write(possible_streams[0])
except Exception as e:
    st.write("No One-hot encoded data available")

# DGIM-implementation
container = {}
windowsize = window_length  #aslinda window_length
timestamp = 0
updateinterval = windowsize  # no larger than the window size
updateindex = 0

keysnum = int(math.log(windowsize, 2)) + 1
keylist = list()
# initialize the container
for i in range(keysnum):
    key = int(math.pow(2, i))
    keylist.append(key)
    container[key] = list()

with open('stream.txt', 'w') as f:
    for i in possible_streams[1][choose_stream]:
        f.write(str(i))
actual_count = 0
with open('stream.txt', 'r') as sfile:
    while True:
        char = sfile.read(1)
        if not char:  # no more input
            end_result_dgim = OutputResult(container, keylist, windowsize)
            break
        timestamp = (timestamp + 1) % windowsize
        for k in container.keys():
            for itemstamp in container[k]:
                if itemstamp == timestamp:  # remove record which is out of the window
                    container[k].remove(itemstamp)
        if char == "1":  # add it to the container
            actual_count += 1
            container[1].append(timestamp)
            UpdateContainer(container, keylist, keysnum)
        updateindex = (updateindex + 1) % updateinterval
        if updateindex == 0:
            OutputResult(container, keylist, windowsize)
            print("\n")

subheader_1 = st.subheader("Results")
result_part = st.text("Result of the DGIM Algorithm and comparison to actual number of ones.")
entry = st.text("You have chosen the "+ column_sel + " column and the following category: " + choose_stream_1[1]+".")
result_dgim = st.text("According to DGIM, there are " + str(int(end_result_dgim)) + " ones in the column.")
actual_ones = st.text("Actual number of ones in the column is " + str(actual_count)+".")
error_r = round(abs((actual_count - end_result_dgim)/actual_count), 2)
error_rate = st.text("The error rate is at " + str(error_r)+"%.")

print("DGIM result: " + str(end_result_dgim))
print("Actual count: " + str(actual_count))