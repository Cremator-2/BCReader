# BCReader

The task of this work was to speed up the reading of barcodes in order to avoid delays on an automatic conveyor line in a warehouse. 
Thus, passing the cargo without stopping while reading the barcode in a random place of the cargo.
The problem is solved by preliminary detection of the location of the barcode.
Thus, the number of processed pixels is reduced.
The program provides for the need to capture multiple frames for processing. Then the barcode is detected. 
Then the selected areas are rotated by a given angle a given number of times. 
This is necessary in order to solve the problem of reading barcodes rotated at an arbitrary angle.
The reading itself takes place when a TCP/IP heartbeat is received from the WMS (Warehouse Management System).
In this work, WMS is modeled by the script test_server.py. Where the BCReader.py program is the client.
Implemented the ability to log data. "detect_barcode" is needed for debugging detection parameters.

![image](https://user-images.githubusercontent.com/112019541/187093523-7f3e5285-e8cd-4b57-af8e-6bd312fc3142.png)

