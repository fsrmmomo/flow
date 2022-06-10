#include <stdio.h>
#include <stdint.h>
#if _WIN32
#include <winsock2.h>
#include <ws2tcpip.h>
#pragma comment(lib,"ws2_32.lib")
#elif __linux__
#include <netinet/in.h>
#include <arpa/inet.h>
#endif
#include <pthread.h>
#include <unistd.h>
#include <time.h>
#include "BoBHash32.h"
#include "Htable.h"



int readn(int fd, char* buf, int size)
{
    char* pt = buf;
    int count = size;
    while (count > 0)
    {
        int len = recv(fd, pt, count, 0);
        if (len == -1)
        {
            return -1;
        }
        else if (len == 0)
        {
            return size - count;
        }
        pt += len;
        count -= len;
    }
    return size;
}
//  回调函数(传入clientfd)
void *client_routine(void *arg)
{
    //初始化一个工作套接字
//    int clientfd = *(int *)arg;
    parameter * p = (parameter *)arg;
    int clientfd = p->fd;
    Htable *table = p->htable;

    while(1)
    {
        char buffer[1024] = {0};
        char len[4] = {0};
        //接收信息
        int len1 = recv(clientfd, len, 4, 0);
        if(len1>0){

//            struct timeval start,end;
//            gettimeofday(&start, NULL );
            clock_t start = clock();
            int length = *(int *)len;
            printf("len = %d\n",length);
            char *buf = (char*)malloc(length+4);
            int len2 = readn(clientfd,buf,length);
            if(len2 != length)
            {
#if _WIN32
                closesocket(clientfd);
#elif __linux__
                close(clientfd);
                printf("closed");
#endif
                free(buf);
                break;
            }
            uint32_t * keys = (uint32_t*)buf;
            int int_len = length/sizeof(int);
            int count = 0;
            uint8_t tos = 1;
            tos = (uint8_t)(tos|1);
            if(*keys==0xFFFFFFFF){
                printf("clear big_table");
                table->Clear(table);
                keys++;
            } else{
                table->Insert(table,*keys);
                count += table->Check(table,*keys);
            }
            for (int j = 0; j < int_len-1; ++j) {
                table->Insert(table,*keys);
                count += table->Check(table,*keys);
                //        key = *keys;
                //        keys++;
//            printf("%u\n",*keys);

                keys++;
            }
            free(buf);

            printf("%d\n", count);
            printf("the running time is :%fs\n", (double)(clock() -start)/(double)CLOCKS_PER_SEC); //秒
        } else{
            printf("connect closed\n");
#if _WIN32
            closesocket(clientfd);
#elif __linux__
            close(clientfd);
#endif
            break;
        }
    }
}

#if _WIN32
#elif __linux__
#endif
void *tcp_server(void *arg){
#if _WIN32
    //初始化WSA
    WORD sockVersion = MAKEWORD(2, 2);
    WSADATA wsaData;
    if (WSAStartup(sockVersion, &wsaData) != 0)
    {
        return 0;
    }

    //创建套接字
    SOCKET slisten = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (slisten == INVALID_SOCKET)
    {
        printf("socket error !");
        return 0;
    }
#elif __linux__
    int slisten = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (slisten <0)
    {
        printf("socket error !");
        return 0;
    }
#endif


//    int tcp_server = socket(AF_INET, SOCK_STREAM, 0);

    // 2. 绑定本地的相关信息，如果不绑定，则系统会随机分配一个端口号
    struct sockaddr_in local_addr = {0};
    local_addr.sin_family = AF_INET;		                    // 设置地址族为IPv4
    local_addr.sin_port = htons(8003);	                        // 设置地址的端口号信息
    local_addr.sin_addr.s_addr = inet_addr("192.168.1.99");	//　设置IP地址
    int ret = bind(slisten, (const struct sockaddr *)&local_addr, sizeof(local_addr));
    if (ret < 0)
        perror("bind");
    else
        printf("bind success.\n");

    // 3、listen监听端口，阻塞，等待客户端来连接服务器
    //开始监听
#if _WIN32
    if (listen(slisten, 5) == SOCKET_ERROR)
    {
        printf("listen error !");
        return 0;
    }
#elif __linux__
    if (listen(slisten, 5) <0)
    {
        printf("listen error !");
        return 0;
    }
#endif
    Htable * table = (Htable *)arg;
    while(1)
    {   //初始化接收
        struct sockaddr_in client_addr;
        memset(&client_addr, 0, sizeof(struct sockaddr_in));
        socklen_t client_addr_len = sizeof(client_addr);

        //接收一个请求返回一个套接字clientfd
        int clientfd = accept(slisten, (struct sockaddr*)&client_addr, &client_addr_len);
        printf("Client from %s:%d \n",inet_ntoa(*(struct in_addr*)&client_addr.sin_addr.s_addr),ntohs(client_addr.sin_port));
        //回调处理
        pthread_t thread_id;
        parameter p = {clientfd,table};
        pthread_create(&thread_id, NULL, client_routine, &p);
    }


}

int main() {
    //创建hash计算器
    BoBHash32 boBHash32;
    Init_BobHash32(&boBHash32,739);
    uint32_t key = 10;
    uint32_t res = boBHash32.Run(&boBHash32,(const char*)(&key),KEY_LENGTH);
    printf("%u\n",res);

    //创建htable


    Htable table;
    Init_Htable(&table,10000);
//    for (int i = 0; i < 100000000; ++i){
//        table.Insert(&table,i);
//    }
//    tcp_server();
    pthread_t thread_id;
    pthread_create(&thread_id, NULL, tcp_server,&table);
    sleep(50000);
//    table.Insert(&table,555);
//    table.Insert(&table,666);
////    printf("创建hash表\n");
//    printf("%d\n",table.Check(&table,555));
//    printf("%d\n",table.Check(&table,666));
//    table.Clear(&table);
//    printf("%d\n",table.Check(&table,555));
//    printf("%d\n",table.Check(&table,666));
    return 0;
}
