"""
Приведите пример кода, для которого невозможно написать юнит-тесты. 
Пример должен содержать минимум 3 класса.
"""
# God object + Singleton

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance


@singleton
class CatDogGod():
    def __init__(self, religion):
        self.religion = religion
        self.list_of_critters = []

        self.main()
        
    class Cat:
        def __init__(self, breed):
            self.breed = breed

        def born(self):
            self.say()
        
        def die(self):
            self.say()
            
        def say(self):
            print("meow")

    class Dog:
        def __init__(self, breed):
            self.breed = breed

        def born(self):
            self.say()
        
        def die(self):
            self.say()
            
        def say(self):
            print("wow")
        

    def create_cat(self, breed):
        self.list_of_critters.append(self.Cat(breed))
        self.list_of_critters[-1].born()
        return self.list_of_critters[-1]

    def create_dog(self, breed):
        self.list_of_critters.append(self.Dog(breed))
        self.list_of_critters[-1].born()
        return self.list_of_critters[-1]   

    def start_world(self):
        self.create_cat("Maine coon")
        self.create_dog("Siberian Husky")

    def stop_world(self):
        while len(self.list_of_critters) != 0:
            self.list_of_critters[-1].die()
            self.list_of_critters.pop()

    def main(self):
        self.start_world()

        for crit in self.list_of_critters:
            crit.say()

        self.stop_world()
        

if __name__ == "__main__":
    CatDogGod("Buddhism")



