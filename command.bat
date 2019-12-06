protoc  -I=simple --python_out=simple\ simple\*.proto
protoc  -I=addressbook --python_out=addressbook\  addressbook\*.proto
protoc  -I=pdcpDaemon\ --python_out=pdcpDaemon\ pdcpDaemon\*.proto
protoc  -I=pdcpDaemon5G\protoFiles\ --python_out=pdcpDaemon5G\ pdcpDaemon5G\protoFiles\*.proto