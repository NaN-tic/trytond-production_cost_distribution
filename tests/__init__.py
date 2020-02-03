# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
try:
    from trytond.modules.production_cost_distribution.tests.test_production_cost_distribution import suite
except ImportError:
    from .test_production_cost_distribution import suite

__all__ = ['suite']
