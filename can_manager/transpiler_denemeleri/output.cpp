#include <iostream>
#include <string>
#include <vector>

class CAN1 {
public:
    int output1;
    int output2;
    CAN1() {
        output1 = 16; // Bits 0-4
        output2 = 8; // Bits 4-8
    }
};

class CAN2 {
public:
    int output1;
    int output2;
    CAN2() {
        output1 = 32; // Bits 0-8
        output2 = 64; // Bits 8-16
    }
};

int MAN1(int input1, int input2) {
    int output1 = input1 + ((input2 & 240) >> 4);
    return output1;
}

int MAN2(int input1) {
    int output1 = ((input1 & 3) >> 0);
    return output1;
}

signed int VAR1;
int VAR2;
int VAR3;

int main() {
    CAN1 can1;
    CAN2 can2;

    int result_MAN1_0 = MAN1(can1.output2, can1.output2);
    int result_MAN1_1 = MAN1(can2.output1, can2.output1);
    VAR1 = result_MAN1_0;
    // Warning: result_MAN2_0 not defined before use
    // VAR2 = result_MAN2_0;
    int result_MAN2_0 = MAN2(can1.output1);
    
    // Ekrana bastırmayı ben yaptım
    printf("%d\n", result_MAN1_0);
    printf("%d\n", result_MAN1_1);
    printf("%d\n", result_MAN2_0);

    return 0;
}
