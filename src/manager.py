from src.models import Apartment, Bill, Parameters, Tenant, Transfer


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key: str, year: int | None = None, month: int | None = None) -> float:
        if apartment_key not in self.apartments:
            raise ValueError(f"Apartment '{apartment_key}' does not exist")
        
        if month is not None and not (1 <= month <= 12):
            raise ValueError(f"Invalid month: {month}")

        total_cost = 0.0
        for bill in self.bills:
            if bill.apartment == apartment_key:
                if year is not None and bill.settlement_year != year:
                    continue
                if month is not None and bill.settlement_month != month:
                    continue
                total_cost += bill.amount_pln
                
        return total_cost