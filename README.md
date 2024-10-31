# Cache_TCP_UDP
Implemetation of Cache with reliable data transfer using socket programming (Both TCP and UDP)


This application allows users to upload and download files using a cache mechanism. The application consists of three main components: a client, a server, and a cache. File downloads first check the cache for local availability; if the file is not present, the server is contacted. File uploads go directly to the server, bypassing the cache.

**File Upload:** Users can upload files directly to the server.

**File Download**: Users can download files, but application first checks the cache for availability. If not available in cache then it downloads the file from the server saving a copy in the cache for future downloads.

**Transport Layer Options**: Supports two types of data transport .User can select based on their choice
1) TCP 
2) Stop-and-Wait protocol over UDP
