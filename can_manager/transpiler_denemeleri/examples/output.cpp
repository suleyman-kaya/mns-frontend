#include <iostream>
#include <string>
#include <vector>
#include <bitset>
#include <cstdint>

template<typename T, size_t M>
T extract_bits(T input, int start, int end) {
    T mask = ((static_cast<T>(1) << (end - start + 1)) - 1) << start;
    return (input & mask) >> start;
}

class CAN_Message_0 {
public:
    std::bitset<4> output1;
    std::bitset<4> output2;
    std::string id;
    bool isStd;
    CAN_Message_0() {
        id = "faae73";
        isStd = true;
    }
    int8_t get_output1() const {
        return static_cast<int8_t>(extract_bits<int8_t, 4>(output1.to_ullong(), 0, 3));
    }
    int8_t get_output2() const {
        return static_cast<int8_t>(extract_bits<int8_t, 4>(output2.to_ullong(), 4, 7));
    }
};

class CAN_Message_1 {
public:
    float output1;
    float output2;
    std::string id;
    bool isStd;
    CAN_Message_1() {
        id = "ed7cf7";
        isStd = false;
    }
    float get_output1() const {
        return output1;
    }
    float get_output2() const {
        return output2;
    }
};

int8_t Int8_t_Adder(int8_t input1, int8_t input2) {
    int8_t output1 = input1 + input2;
    return output1;
}

float Float_Adder(float input1, float input2) {
    float output1 = input1 + input2;
    return output1;
}

double Float_Int_Adder(double input1, double input2) {
    double output1 = input1 + input2;
    return output1;
}

int8_t Result_0;
float Result_1;
double Result_2;

int main() {
    CAN_Message_0 can_message_0;
    CAN_Message_1 can_message_1;

    int8_t result_Int8_t_Adder_0 = Int8_t_Adder(can_message_0.get_output1(), can_message_0.get_output1());
    int8_t result_Int8_t_Adder_1 = Int8_t_Adder(can_message_0.get_output2(), can_message_0.get_output2());
    float result_Float_Adder_0 = Float_Adder(can_message_1.get_output1(), can_message_1.get_output1());
    float result_Float_Adder_1 = Float_Adder(can_message_1.get_output2(), can_message_1.get_output2());
    Result_0 = result_Int8_t_Adder_0;
    Result_1 = result_Float_Adder_0;
    // Warning: result_Float_Int_Adder_0 not defined before use
    // Result_2 = result_Float_Int_Adder_0;

    return 0;
}
