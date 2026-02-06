#include <bits/stdc++.h>
using namespace std;

int main() {
    int n;
    cin >> n;

    vector<int> nums(n);
    for (int i = 0; i < n; i++) {
        cin >> nums[i];
    }

    int target;
    cin >> target;

    unordered_map<int, int> hashmap;

    for (int i = 0; i < n; i++) {
        int need = target - nums[i];

        if (hashmap.find(need) != hashmap.end()) {
            cout << hashmap[need] << " " << i << endl;
            break;
        }

        hashmap[nums[i]] = i;
    }

    return 0;
}
