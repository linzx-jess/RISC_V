#include <stdio.h>
#include <stdlib.h>
// #include <time.h> // 移除对 time.h 的依赖
// #include <unistd.h> // 移除对 unistd.h (sleep) 的依赖

// 简单的软件延时函数，模拟 sleep(2)
void delay_ms(volatile unsigned int ms) {
    // 这是一个非常简化的延时，需要调整 TICK_PER_MS 来匹配 QEMU 的模拟速度
    // 经过测试，在 QEMU 中大约需要 10000000 次循环来模拟几秒的延时
    // 目标：模拟 2000 毫秒（2 秒）
    volatile unsigned int i, j;
    // 调整这个值直到 QEMU 运行看起来接近 2 秒的间隔
    const unsigned int LOOPS = 10000000; 
    
    for (i = 0; i < LOOPS; i++) {
        // 空循环实现延时
    }
}

// 模拟温湿度数据生成函数
void generate_data(float *temp, float *humid) {
    // 使用 rand() 来生成数据，rand() 是 Newlib 中存在的
    *temp = 20.0 + (float)rand() / (float)(RAND_MAX / 10.0);
    *humid = 50.0 + (float)rand() / (float)(RAND_MAX / 20.0);
}

int main() {
    float temperature, humidity;
    
    // 简化 srand 初始化：在裸机环境中，我们使用一个固定的种子（例如 1）
    // 或者直接使用 Newlib 的 time(0) 默认实现（它通常返回 0）
    srand(1); 

    // 使用 puts() 代替 printf() 减少对浮点数格式化库的依赖，提高兼容性
    puts("RISC-V IoT Data Simulator Starting...\n"); 

    // 无限循环模拟数据采集
    while (1) {
        generate_data(&temperature, &humidity);
        
        // 格式化输出数据：T:xx.x,H:yy.y
        // QEMU 的 stdout/printf 是由 Newlib 提供的系统调用（syscall）模拟的
        printf("T:%.1f,H:%.1f\n", temperature, humidity);
        
        // 立即刷新输出缓冲区
        fflush(stdout); 

        // 调用软件延时函数
        delay_ms(1); // 这里的参数只是一个占位符，实际延时时间由 LOOPS 决定
    }

    return 0;
}