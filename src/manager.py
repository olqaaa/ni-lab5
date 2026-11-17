from src.models import Apartment, ApartmentSettlement, Bill, Parameters, Tenant, Transfer, TenantSettlement


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

    def get_apartment_costs(self, apartment_key: str, year: int | None = None, month: int | None = None) -> float | None:
        if apartment_key not in self.apartments:
            return None
        
        if month is not None and not (1 <= month <= 12):
            return None

        total_cost = 0.0
        for bill in self.bills:
            if bill.apartment == apartment_key:
                if year is not None and bill.settlement_year != year:
                    continue
                if month is not None and bill.settlement_month != month:
                    continue
                total_cost += bill.amount_pln
                
        return total_cost

    def create_apartment_settlement(self, apartment_key: str, year: int, month: int) -> ApartmentSettlement | None:
        if apartment_key not in self.apartments:
            return None

        total_bills = self.get_apartment_costs(apartment_key, year, month)
        if total_bills is None:
            return None

        target_ym = f"{year:04d}-{month:02d}"
        total_rent = 0.0
        for tenant in self.tenants.values():
            if tenant.apartment == apartment_key:
                if tenant.date_agreement_from[:7] <= target_ym <= tenant.date_agreement_to[:7]:
                    total_rent += tenant.rent_pln

        return ApartmentSettlement(
            apartment=apartment_key,
            month=month,
            year=year,
            total_rent_pln=total_rent,
            total_bills_pln=total_bills,
            total_due_pln=total_rent + total_bills
        )

    def create_tenant_settlements(self, apartment_settlement: ApartmentSettlement) -> list[TenantSettlement]:
        target_ym = f"{apartment_settlement.year:04d}-{apartment_settlement.month:02d}"

        active_tenants = [
            (tenant_key, tenant)
            for tenant_key, tenant in self.tenants.items()
            if tenant.apartment == apartment_settlement.apartment
            and tenant.date_agreement_from[:7] <= target_ym <= tenant.date_agreement_to[:7]
        ]

        if not active_tenants:
            return []

        bills_per_tenant = apartment_settlement.total_bills_pln / len(active_tenants)
        settlements = []

        for tenant_key, tenant in active_tenants:
            total_due = tenant.rent_pln + bills_per_tenant
            settlements.append(TenantSettlement(
                tenant=tenant_key,
                apartment_settlement=apartment_settlement.apartment,
                month=apartment_settlement.month,
                year=apartment_settlement.year,
                rent_pln=tenant.rent_pln,
                bills_pln=bills_per_tenant,
                total_due_pln=total_due,
                balance_pln=total_due
            ))

        return settlements