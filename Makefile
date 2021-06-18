
sources= jtt808_send_recv_packet.c jtt808_netutil.c  jtt808_convert.c jtt808_action.c jtt808_basic_check.c

test_accelration_c1:
	gcc $(sources) -g -DJTT808_TEST_REGISTER=1 -DJTT808_TEST_PRINT_SEND_PACKET=1 -DJTT808_TEST_SEND_ACCELERATION_C1=1
	./a.out

test_accelration_a1:
	gcc $(sources) -g -DJTT808_TEST_REGISTER=1 -DJTT808_TEST_PRINT_SEND_PACKET=1 -DJTT808_TEST_SEND_ACCELERATION_A1=1
	./a.out

test_position:
	gcc $(sources) -g -DJTT808_TEST_REGISTER=1 -DJTT808_TEST_PRINT_SEND_PACKET=1 -DJTT808_TEST_SEND_POSITION_PACKET=1
	./a.out

test_reigster:
	gcc $(sources) -g -DJTT808_TEST_REGISTER=1 -DJTT808_TEST_PRINT_SEND_PACKET=1 -DJTT808_TEST_SEND_HEART_PACKET=1
	./a.out

main_send:
	gcc $(sources) -g -DJTT808_TEST_SEND_PACKET=1
	./a.out

main_recv:
	gcc $(sources) -g -DJTT808_TEST_RECV_PACKET=1
	./a.out

clean:
	rm a.out
