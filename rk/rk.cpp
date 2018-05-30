/* Приведите 3 примера(с кодом) сопряжения, которые использовать не желательно.*/
class MyMoney 
{  
    public:
        int account_on_purse; //private, завести три отдельных класса: MyMoney, Purse, Bank_Acc
        int account_on_bank;
        int income();
        int expenses();
        int pay_from_purse();
        int pay_from_bank();

};

class Attacker
{
    public: 
    void steal_money(MyMoney *m) {
        m->account_on_bank = 0;
        m->account_on_purse = 0;
    };

};