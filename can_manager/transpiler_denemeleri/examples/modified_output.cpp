#include <iostream>
#include <string>
#include <bitset>
#include <cstdint>
#include <cstring>

// Function to extract bits from a bitset
template<typename T, size_t M>
T extract_bits(T input, int start, int end) {
    T mask = ((static_cast<T>(1) << (end - start + 1)) - 1) << start;
    return (input & mask) >> start;
}

class CAN_Message_0 {
public:
    std::bitset<8> output;
    std::string id;
    bool isStd;

    CAN_Message_0() {
        id = "faae73";
        isStd = true;
        output = std::bitset<8>("10100110");  // örnek olarak 10 ve 6 (1010 ve 0110) bitleri yan yana
    }

    int8_t get_output1() const {
        return static_cast<int8_t>(extract_bits<int8_t, 8>(output.to_ullong(), 4, 7));
    }

    int8_t get_output2() const {
        return static_cast<int8_t>(extract_bits<int8_t, 8>(output.to_ullong(), 0, 3));
    }
};

class CAN_Message_1 {
public:
    std::bitset<64> output; // 32-bit floatlar için daha büyük bitset kullanıyoruz
    std::string id;
    bool isStd;

    CAN_Message_1() {
        id = "ed7cf7";
        isStd = false;
        float f1 = 3.14f; // float 3.14
        float f2 = 1.59f; // float 1.59
        uint32_t int_rep_f1;
        uint32_t int_rep_f2;
        std::memcpy(&int_rep_f1, &f1, sizeof(f1));
        std::memcpy(&int_rep_f2, &f2, sizeof(f2));
        output = (static_cast<uint64_t>(int_rep_f1) << 32) | int_rep_f2;
    }

    float get_output1() const {
        uint32_t int_rep = static_cast<uint32_t>(extract_bits<uint64_t, 64>(output.to_ullong(), 32, 63));
        float result;
        std::memcpy(&result, &int_rep, sizeof(result));
        return result;
    }

    float get_output2() const {
        uint32_t int_rep = static_cast<uint32_t>(extract_bits<uint64_t, 64>(output.to_ullong(), 0, 31));
        float result;
        std::memcpy(&result, &int_rep, sizeof(result));
        return result;
    }
};

int8_t Int8_t_Adder(int8_t input1, int8_t input2) {
    return input1 + input2;
}

float Float_Adder(float input1, float input2) {
    return input1 + input2;
}

double Float_Int_Adder(double input1, double input2) {
    return input1 + input2;
}

int main() {
    CAN_Message_0 can_message_0;
    CAN_Message_1 can_message_1;

    int8_t result_Int8_t_Adder = Int8_t_Adder(can_message_0.get_output1(), can_message_0.get_output2());
    float result_Float_Adder = Float_Adder(can_message_1.get_output1(), can_message_1.get_output2());

    double result_Float_Int_Adder = Float_Int_Adder(static_cast<double>(result_Int8_t_Adder), static_cast<double>(result_Float_Adder));

    // 4-bit işaretli sayıların doğru şekilde alınabilmesi için eklemeler
    auto to_signed_4bit = [](int8_t val) -> int8_t {
        return val > 7 ? val - 16 : val; // 4-bit işaretli sayılar için dönüştürme
    };

    std::cout << "CAN Message 0:" << std::endl;
    std::cout << "  ID: " << can_message_0.id << std::endl;
    std::cout << "  Standard: " << (can_message_0.isStd ? "Yes" : "No") << std::endl;
    std::cout << "  Output (Combined): " << can_message_0.output << std::endl;
    std::cout << "  Output 1: " << static_cast<int>(to_signed_4bit(can_message_0.get_output1())) << std::endl;
    std::cout << "  Output 2: " << static_cast<int>(to_signed_4bit(can_message_0.get_output2())) << std::endl;

    std::cout << "CAN Message 1:" << std::endl;
    std::cout << "  ID: " << can_message_1.id << std::endl;
    std::cout << "  Standard: " << (can_message_1.isStd ? "Yes" : "No") << std::endl;
    std::cout << "  Output (Combined): " << can_message_1.output << std::endl;
    std::cout << "  Output 1: " << can_message_1.get_output1() << std::endl;
    std::cout << "  Output 2: " << can_message_1.get_output2() << std::endl;

    std::cout << "Results:" << std::endl;
    std::cout << "  Int8_t Adder: " << static_cast<int>(to_signed_4bit(result_Int8_t_Adder)) << std::endl;
    std::cout << "  Float Adder: " << result_Float_Adder << std::endl;
    std::cout << "  Float-Int Adder: " << result_Float_Int_Adder << std::endl;

    return 0;
}
