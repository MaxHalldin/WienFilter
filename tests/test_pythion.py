from pythion import MainWindow
from pythion.connections import RS3000Output, PortSelector


def test_main() -> None:
    assert MainWindow._instance is None


def test_rs() -> None:
    MAX_VOLTAGE_RS = 30
    port_rs = PortSelector.get_port_of('rs')
    if port_rs is None:
        port_rs = ''

    rs = RS3000Output(port=port_rs, voltage_limit=MAX_VOLTAGE_RS)
    assert rs._to_voltage_string(0) == '00.00'
    assert rs._to_voltage_string(1) == '01.00'
    assert rs._to_voltage_string(1.1) == '01.10'
    assert rs._to_voltage_string(1.10) == '01.10'
    assert rs._to_voltage_string(1.13) == '01.13'
    assert rs._to_voltage_string(1.104) == '01.10'
    assert rs._to_voltage_string(1.16645) == '01.17'
    assert rs._to_voltage_string(21) == '21.00'
    assert rs._to_voltage_string(11.245) == '11.24'
    assert rs._to_voltage_string(11.245000000000001) == '11.25'

    assert rs._to_current_string(0) == '0.000'
    assert rs._to_current_string(1) == '0.001'
    assert rs._to_current_string(12) == '0.012'
    assert rs._to_current_string(10) == '0.010'
    assert rs._to_current_string(110) == '0.110'
    assert rs._to_current_string(999) == '0.999'
    assert rs._to_current_string(1004) == '1.004'
    assert rs._to_current_string(1166.45) == '1.166'
    assert rs._to_current_string(2100) == '2.100'
    assert rs._to_current_string(1124.5) == '1.125'
