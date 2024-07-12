#include <iostream>
#include <string>
#include <vector>
#include <bitset>
#include <cstdint>

template<size_t M>
uint64_t extract_bits(uint64_t input, int start, int end) {
    uint64_t mask = ((1ULL << (end - start + 1)) - 1) << start;
    return (input & mask) >> start;
}

class CAN1 {
public:
    std::bitset<9> output;
    CAN1() {
        output.reset();
    }
    std::bitset<5> get_output1() const {
        return extract_bits<5>(output.to_ullong(), 0, 4);
    }
    std::bitset<5> get_output2() const {
        return extract_bits<5>(output.to_ullong(), 4, 8);
    }
};

class CAN2 {
public:
    std::bitset<17> output;
    CAN2() {
        output.reset();
    }
    std::bitset<9> get_output1() const {
        return extract_bits<9>(output.to_ullong(), 0, 8);
    }
    std::bitset<9> get_output2() const {
        return extract_bits<9>(output.to_ullong(), 8, 16);
    }
};

uint64_t MAN1(uint64_t input1, uint64_t input2) {
    uint64_t output1 = input1 + extract_bits<5>(2, 4, 8);
    return output1;
}

uint64_t MAN2(uint64_t input1) {
    uint64_t output1 = extract_bits<3>(1, 0, 2);
    return output1;
}

int64_t VAR1;
uint64_t VAR2;
uint64_t VAR3;

int main() {
    CAN1 can1;
    CAN2 can2;

    // Örnek test verileri
    can1.output = std::bitset<9>("111111101");
    can2.output = std::bitset<17>("11011011011011011");  // 112171

    std::cout << "CAN1 output: " << can1.output << std::endl;
    std::cout << "CAN1 get_output1: " << can1.get_output1() << std::endl;
    std::cout << "CAN1 get_output2: " << can1.get_output2() << std::endl;

    std::cout << "CAN2 output: " << can2.output << std::endl;
    std::cout << "CAN2 get_output1: " << can2.get_output1() << std::endl;
    std::cout << "CAN2 get_output2: " << can2.get_output2() << std::endl;

    uint64_t result_MAN1_0 = MAN1(can1.get_output2().to_ullong(), can1.get_output2().to_ullong());
    uint64_t result_MAN1_1 = MAN1(can2.get_output1().to_ullong(), can2.get_output1().to_ullong());
    VAR1 = result_MAN1_0;

    std::cout << "Result MAN1 (CAN1 output2): " << result_MAN1_0 << std::endl;
    std::cout << "Result MAN1 (CAN2 output1): " << result_MAN1_1 << std::endl;

    uint64_t result_MAN2_0 = MAN2(can1.get_output1().to_ullong());
    std::cout << "Result MAN2 (CAN1 output1): " << result_MAN2_0 << std::endl;

    return 0;
}
