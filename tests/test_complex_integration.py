import pytest
from src.manager import Manager
from src.models import Parameters
from src.models import Bill
from src.models import ApartmentSettlement

def test_get_apartment_costs():
    parameters = Parameters()
    manager = Manager(parameters)

    assert manager.get_apartment_costs("apart-polanka", 2025, 1) == 910.0

    assert manager.get_apartment_costs("apart-polanka", 2025, 2) == 0.0

    assert manager.get_apartment_costs("apart-polanka", 2024, 1) == 0.0

    assert manager.get_apartment_costs("nieistniejace-mieszkanie", 2025, 1) is None

    assert manager.get_apartment_costs("apart-polanka", 2025, 13) is None




def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0


def test_create_apartment_settlement():
    manager = Manager(Parameters())

    #testowy rachunek dla stycznia 2024
    manager.bills.append(Bill(
        apartment="apart-polanka",
        date_due="2024-02-10",
        settlement_year=2024,
        settlement_month=1,
        amount_pln=300.0,
        type="electricity"
    ))

    #Styczeń 2024 (są najemcy + jest rachunek)
    settlement_with_bills = manager.create_apartment_settlement("apart-polanka", 2024, 1)
    assert isinstance(settlement_with_bills, ApartmentSettlement)
    assert settlement_with_bills.apartment == "apart-polanka"
    assert settlement_with_bills.year == 2024
    assert settlement_with_bills.month == 1
    assert settlement_with_bills.total_rent_pln == 4200.0
    assert settlement_with_bills.total_bills_pln == 300.0
    assert settlement_with_bills.total_due_pln == 4500.0

    #Luty 2024 (są najemcy, ale brak rachunków)
    settlement_no_bills = manager.create_apartment_settlement("apart-polanka", 2024, 2)
    assert isinstance(settlement_no_bills, ApartmentSettlement)
    assert settlement_no_bills.total_rent_pln == 4200.0
    assert settlement_no_bills.total_bills_pln == 0.0
    assert settlement_no_bills.total_due_pln == 4200.0

    #Styczeń 2025 (są rachunki, ale umowy najemców wygasły)
    settlement_2025 = manager.create_apartment_settlement("apart-polanka", 2025, 1)
    assert settlement_2025.total_rent_pln == 0.0
    assert settlement_2025.total_bills_pln == 910.0
    assert settlement_2025.total_due_pln == 910.0

    #nieistniejace mieszkanie 
    assert manager.create_apartment_settlement("nieistniejace", 2024, 1) is None