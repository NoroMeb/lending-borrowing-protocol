def test_pool_logic_constructor(pool_logic, pool_configuration):

    assert pool_logic.poolConfiguration() == pool_configuration
