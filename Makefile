
sources= jtt808_send_recv_packet.c jtt808_netutil.c  jtt808_convert.c
main_send:
	gcc $(sources) -g -DTEST_SEND_PACKET=1
	./a.out

main_recv:
	gcc $(sources) -g -DTEST_RECV_PACKET=1
	./a.out

clean:
	rm a.out
