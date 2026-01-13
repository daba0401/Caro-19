import os
import random
import shutil

# ================= CẤU HÌNH =================
OUTPUT_DIR = "CAU4"
NUM_TESTS = 40
MOD = 10**9 + 7

# ================= SOLVER CHUẨN =================
def get_all_divisors(arr):
    divs = set()
    for x in arr:
        i = 1
        while i * i <= x:
            if x % i == 0:
                divs.add(i)
                divs.add(x // i)
            i += 1
    return sorted(divs)

def solve(n, a):
    D = get_all_divisors(a)

    dp = [0] * (n + 1)
    dp[1] = 1

    for i in range(1, n + 1):
        if dp[i] == 0:
            continue
        for d in D:
            j = i + d
            if j <= n:
                dp[j] = (dp[j] + dp[i]) % MOD

    return dp[n]

# ================= SINH TEST =================
def generate_tests():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    print(f"Đang tạo {NUM_TESTS} test CAU4...")

    for t in range(1, NUM_TESTS + 1):
        test_dir = os.path.join(OUTPUT_DIR, f"Test{t:02d}")
        os.makedirs(test_dir)

        # ---- Test ví dụ ----
        if t == 1:
            n = 5
            k = 1
            a = [3]

        # ---- Subtask 1: 40% ----
        elif t <= 16:
            n = random.randint(2, 20)
            k = 1
            a = [6]

        # ---- Subtask 2: 60% ----
        else:
            if t <= 25:
                n = random.randint(50, 500)
            elif t <= 35:
                n = random.randint(1000, 5000)
            else:
                n = random.randint(20000, 100000)

            k = random.randint(1, 10)
            a = []

            for _ in range(k):
                r = random.random()
                if r < 0.3:
                    a.append(random.randint(2, 20))      # ít ước
                elif r < 0.6:
                    a.append(random.randint(100, 1000))  # trung bình
                else:
                    a.append(random.randint(100000, 1000000))  # nhiều ước

        # ---- GHI FILE ----
        with open(os.path.join(test_dir, "CAU4.INP"), "w") as f:
            f.write(f"{n} {k}\n")
            f.write(" ".join(map(str, a)))

        ans = solve(n, a)

        with open(os.path.join(test_dir, "CAU4.OUT"), "w") as f:
            f.write(str(ans))

        print(f"Test {t:02d}: N={n}, K={k}, Ans={ans}")

    print("HOÀN TẤT!")

if __name__ == "__main__":
    generate_tests()
