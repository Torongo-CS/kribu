from kribu import is_prime


def test_is_prime_via_cpp():
    # This calls the C++ nanobind function
    assert is_prime(2)
    assert not is_prime(4)
    assert is_prime(17)
    assert not is_prime(18)
