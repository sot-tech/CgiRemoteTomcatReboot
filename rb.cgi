#!/bin/bash

#Copyright (c) 2016, sot
#All rights reserved.
#
#Redistribution and use in source and binary forms, with or without
#modification, are permitted provided that the following conditions are met:
#
#* Redistributions of source code must retain the above copyright notice, this
#  list of conditions and the following disclaimer.
#* Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#
#THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
#IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
#ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
#LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
#CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
#SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
#INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
#CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
#POSSIBILITY OF SUCH DAMAGE.

SERVERS="NAME0:IP0 NAME1:IP1"

STATUSES="000 UNDEFINED
100 Continue
101 Switching Protocols
102 Processing
200 OK
201 Created
202 Accepted
203 Non-authoritative Information
204 No Content
205 Reset Content
206 Partial Content
207 Multi-Status
208 Already Reported
226 IM Used
300 Multiple Choices
301 Moved Permanently
302 Found
303 See Other
304 Not Modified
305 Use Proxy
307 Temporary Redirect
308 Permanent Redirect
400 Bad Request   
401 Unauthorized   
402 Payment Required   
403 Forbidden   
404 Not Found   
405 Method Not Allowed   
406 Not Acceptable   
407 Proxy Authentication Required   
408 Request Timeout   
409 Conflict   
410 Gone   
411 Length Required   
412 Precondition Failed   
413 Payload Too Large   
414 Request-URI Too Long   
415 Unsupported Media Type   
416 Requested Range Not Satisfiable   
417 Expectation Failed   
418 I'm a teapot   
421 Misdirected Request   
422 Unprocessable Entity   
423 Locked   
424 Failed Dependency   
426 Upgrade Required   
428 Precondition Required   
429 Too Many Requests   
431 Request Header Fields Too Large   
444 Connection Closed Without Response   
451 Unavailable For Legal Reasons   
499 Client Closed Request   
500 Internal Server Error   
501 Not Implemented   
502 Bad Gateway   
503 Service Unavailable   
504 Gateway Timeout   
505 HTTP Version Not Supported   
506 Variant Also Negotiates   
507 Insufficient Storage   
508 Loop Detected   
510 Not Extended   
511 Network Authentication Required   
599 Network Connect Timeout Error"

read POST_STRING

echo "Content-type: text/html"
echo ""
echo "<html><head><title>REBOOT</title></head><body>"
echo '<meta http-equiv="Content-Type" content="text/html; charset=UTF-8">'


for server in $SERVERS; do
	NAME=$(echo $server | tr ':' ' ' | awk '{print $1}')
	ADDRESS=$(echo $server | tr ':' ' ' | awk '{print $2}')
	CMD_BASE="ssh root@$ADDRESS -i /var/www/.ssh/id_rsa"
	echo "<h1>Состояние сервера $NAME</h1>"
	echo "<h2>Свободное место</h2>"
	$CMD_BASE df -h /dev/sda2 --output=avail
	echo "<br>"
	$CMD_BASE df -h /dev/sda2 --output=size
	echo "<br>"
	echo "<h2>Статус демона</h2>"
	$CMD_BASE service tomcat status 2>&1 | grep "^   Active:"
	echo "<br>"
	echo "<h2>Статус порта</h2>"
	nmap $ADDRESS -p 8080 -Pn | grep "^8080"
	echo "<br>"
	echo "<h2>Статус http</h2>"
	echo "$STATUSES" | grep "^$(curl --connect-timeout 10 -H 'Accept-Language: ru' -L -s -o /dev/null -w "%{http_code}" http://$ADDRESS:8080/cloudserver/auth/login.form)"
	echo "<br><br>"
	#       echo "args: $POST_STRING $QUERY_STRING"
	if echo "$POST_STRING" | sed -n 's/^.*reboot=\([^&]*\).*$/\1/p' | grep $NAME &> /dev/null; then
		$CMD_BASE service tomcat restart;
		echo '<h2>Перезапуск...</h2>'
	else
		echo '<form action="/cgi-bin/rb.cgi" method="post">'
		printf '<button style="font-size : 20px; width: 100%%; height: 100px;" name="reboot" type="submit" value="%s">Перезагрузить %s</button>\n' $NAME $NAME
		echo '</form>'
	fi

done
echo "</body></html>"
