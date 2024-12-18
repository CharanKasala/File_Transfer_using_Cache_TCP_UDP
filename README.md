This project is cache-enabled file transfer system that manages file uploads and downloads between the client, cache, and server. The system first checks if the requested file is cached locally. If not, it retrieves the file from the server and stores it in the cache for future use. The system supports two transport protocols:

TCP (Transmission Control Protocol)

Stop-and-Wait (SNW) Protocol over UDP

<ins>**Features:**</ins>

**Client-Cache-Server Interaction:**

The client interacts with both the cache and the server for file uploads and downloads.

**File Uploads:**

Files uploaded by the client are stored directly on the server, bypassing the cache.

**File Downloads:** 

When a client requests a file, the system first checks the cache. If the file is found, it is served from the cache, minimizing server load. If the file is not in the cache, it is retrieved from the server and cached for future requests.

**Protocol Support:**

The system supports both TCP (for reliable transmission) and the Stop-and-Wait protocol (over UDP), allowing it to adapt to different network conditions.

**Timeout :** 

The Stop-and-Wait protocol includes a timeout feature to handle packet loss, ensuring reliable transmission even in less stable networks.

<ins>**Architecture Design**</ins>

The following image visually represents the interaction between client ,server and cache


![Archtecture design of project](https://github.com/CharanKasala/File_Transfer_using_Cache_TCP_UDP/blob/main/Architecture_Design.jpeg)

<ins>**Instructions:**</ins>

To interact with the file transfer system, the user must enter one of the following commands

**put <file>:** Upload a file from the client to the server.

**get <file>:** Download a file from the cache (if available) or from the server.

**quit:** Exit the program and terminate the connection.


<ins>**Implementation Details:**</ins>

**Caching Logic:**

Before fetching a file from the server, the system first checks the cache for its availability. If the file is found in the cache, it is immediately delivered to the client, minimizing server load and improving efficiency. If the file is not cached, the system queries the server, retrieves the file, and stores it in the cache for future use.

**Transport Layer:**

**TCP (Transmission Control Protocol):**

The system uses TCP to ensure reliable communication. TCP's built-in mechanisms, such as automatic acknowledgment, error detection, and retransmission of lost packets, provide a robust and dependable way to transfer files.

**SNW Protocol (Stop-and-Wait) over UDP:**

The Stop-and-Wait protocol is implemented over UDP to offer a simpler, lightweight transport layer. Custom reliability is achieved through acknowledgment (ACK) messages and timeouts. If a packet is lost or not acknowledged within a certain time frame, the packet is retransmitted, ensuring reliable data transmission over an inherently unreliable protocol like UDP

<ins>**Tech Stack :**</ins>

**Programming Languages:** 

Python

**Transport Protocols:**

TCP

UDP (Stop-and-Wait). 


A custom cache implementation is used for storing files locally. The cache helps reduce server load by serving files from local storage when available, improving the overall efficiency of the file transfer process


**Wireshark:**

Wireshark is used for packet analysis and performance evaluation. It helps capture network traffic, analyze delays, and measure throughput during the file transfer tests.

<ins>**Performance Testing**</ins>

The project includes performance testing to evaluate the efficiency of the file transfer system under different transport protocols (TCP and SNW). **Wireshark** is used to capture and analyze packet exchanges, allowing for a detailed assessment of delay and throughput. The testing aims to compare how each protocol performs in terms of data transfer speed and reliability for different file sizes.

The following files are used in the performance tests:

file1.txt (16KB)

file2.txt (32KB)

file3.txt (48KB)

file4.txt (62KB)

The results from the performance testing are displayed in the tables below, highlighting the differences between TCP and SNW protocols in terms of delay and throughput for different file sizes.

Delay (in seconds)
| File               | TCP (sec)  | SNW (sec)  |
|--------------------|------------|------------|
| **file1.txt (16KB)** | 0.008134   | 0.060079   |
| **file2.txt (32KB)** | 0.030312   | 0.105959   |
| **file3.txt (48KB)** | 0.031905   | 0.172231   |
| **file4.txt (62KB)** | 0.034619   | 0.221626   |

visual representation of Delay for TCP vs UDP is: 

![Delay](https://github.com/CharanKasala/File_Transfer_using_Cache_TCP_UDP/blob/main/Delay.png)

Throughput (in bits per second)

| File               | TCP (bps)         | SNW (bps)          |
|--------------------|-------------------|--------------------|
| **file1.txt (16KB)** | 14,634,866        | 1,981,391          |
| **file2.txt (32KB)** | 7,854,315.123     | 2,246,906.822      |
| **file3.txt (48KB)** | 11,194,233        | 2,073,680          |
| **file4.txt (62KB)** | 13,755,221.12     | 2,148,628.771      |

visual representation of Throughput for TCP vs UDP is: 

![Throughput](https://github.com/CharanKasala/File_Transfer_using_Cache_TCP_UDP/blob/main/Throughput.png)


<ins>**Instructions to execute:**</ins>

1. Clone the repository:

        git clone <repository-url>

2. Navigate to the project directory:

        cd <project-directory>

3.**Run the server:** The server is responsible for storing and serving the files.

        python server.py <port> <protocol>

This will Start the server on the specified `<port>`.
The `<protocol>` can be either tcp or snw (stop-and-wait).

4. **Run the cache:** The cache stores files locally to improve performance by reducing server load.

        python cache.py <port> <server_ip> <server_port> <protocol>
   
This will Start the cache on the specified `<port>`.
Connects to the server using the provided `<server_ip>` and `<server_port>`.
The `<protocol>` can be either tcp or snw but it should be the same  one selected while running the server..

5. **Run the client:** The client uploads and downloads files, interacting with both the cache and the server.

        python client.py <server_ip> <server_port> <cache_ip> <cache_port> <protocol>
   
This will start the client.
Connects to the server using `<server_ip>` and `<server_port>`.
Connects to the cache using `cache_ip>` and `<cache_port>`.
The `<protocol>` can be either tcp or snw but it should be the same one selected while running the server.

7. **Upload a file to the server:** Use the put command to upload a file from the client to the server.

        put <file_path>

7.**Download a file from the cache or server:** Use the get command to download a file. The system first checks the cache, and if the 
    file is not there, it fetches it from the server storing a copy in the cache for future downloads.

        get <file_path>

8.**Quit the program:** Exit the program and terminate the server, cache, and client processes.

        quit
