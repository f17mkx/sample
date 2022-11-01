class Employee:
    """
       Specifies bank accounts and transaction functions.

       Employee(name, department, experience):
           name: name of the employee

       .training(gain):
           adds 'gain' to the employees experience
       """

    # class attributes
    num_of_employees = 0
    #departmentDict = {}

    def __init__(self, name, department, experience):
        """specifies the employee"""
        Employee.num_of_employees += 1
        self.num = Employee.num_of_employees
        self.name = name
        self.department = department
        self.ep = experience
       # Employee.departmentDict[name] = department


    def training(self, gain):
        """trains employee, employee gains 'gain' experience."""
        if not type(gain) == int:
            raise TypeError
        self.ep += gain

    def __str__(self):
        """Return str(self). """
        return f"Employee {self.num}: [{self.name}, department: {self.department}, ep:  {self.ep}]"
