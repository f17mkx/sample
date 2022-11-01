
from employee_class import Employee

if __name__ == "__main__":
    print("Employee application")

    FrankUnderwood = Employee("Frank Underwood", "Management", 1290)
    ParisHilton = Employee("Paris Hilton", "Public Relations", 807)
    HankMoody = Employee("Hank Moody", "Public Relations", 465)
    DonaldTrump = Employee("Donald Trump", "Management", 1152)
    KimKönig = Employee("Kim König", "Public Relations", 239)

    print(FrankUnderwood)
    FrankUnderwood.training(10)
    print(FrankUnderwood.ep)

    ParisHilton.training(400)
    print(ParisHilton)
    ParisHilton.department = "Management"
    print(ParisHilton)

    departmentDictionary = {FrankUnderwood.name: FrankUnderwood.department, ParisHilton.name: ParisHilton.department,
                            HankMoody.name: HankMoody.department, DonaldTrump.name: DonaldTrump.department,
                            KimKönig.name: KimKönig.department}
    print(departmentDictionary)

    for key in departmentDictionary:
        print("<",  departmentDictionary[key], ">","<", key, ">")



