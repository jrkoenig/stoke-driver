
// singlely linked list node
struct node {
  node* next;
  int value;
};

extern "C" {
node* list_reverse(node* n) {
  if (n == nullptr)
    return nullptr;
  node* result = n, *rest = n->next;
  result->next = nullptr;
  while(rest != nullptr) {
    node* temp = rest->next;
    rest->next = result;
    result = rest;
    rest = temp;
  }
  return result;
}

int list_max(node* n) {
  int max = n->value;
  while(n != nullptr) {
    if (n->value > max)
      max = n->value;
    n = n->next;
  }
  return max;
}
}

int main() {
  node nodes[10];
  
  nodes[0].next = &nodes[1];
  nodes[1].next = &nodes[2];
  nodes[2].next = nullptr;
  
  list_reverse(&nodes[0]);
  
  nodes[1].next = &nodes[0];
  nodes[0].next = &nodes[2];
  nodes[2].next = nullptr;
  
  list_reverse(&nodes[1]);
  
  list_reverse(nullptr);
  
  nodes[2].next = nullptr;
  list_reverse(&nodes[2]);
  
  nodes[0].next = &nodes[1];
  nodes[0].value = 3424;
  nodes[1].next = &nodes[8];
  nodes[1].value = 3411;
  nodes[8].next = &nodes[4];
  nodes[8].value = 2514;
  nodes[4].next = &nodes[5];
  nodes[4].value = -2314;
  nodes[5].next = &nodes[2];
  nodes[5].value = 6254;
  nodes[2].next = nullptr;
  nodes[2].value = 1232;
  
  list_max(&nodes[0]);
  list_max(&nodes[8]);
  list_max(&nodes[4]);
  list_max(&nodes[5]);
  list_max(&nodes[2]);
  
}
