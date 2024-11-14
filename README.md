The goal of this project is to develop a cache-enabled file transfer system that manages file uploads and downloads between the client, cache, and server. The system first checks if the requested file is cached locally. If not, it retrieves the file from the server and stores it in the cache for future use. The system supports two transport protocols:


**Overview:**

The objective of this project is to develop a cache-enabled file transfer system that manages file uploads and downloads between the client, cache, and server. The system first checks if the requested file is cached locally. If not, it retrieves the file from the server and stores it in the cache for future use. The system supports two transport protocols:

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
