from services.safety_service import SafetyService
def test_emergency_detection(): assert SafetyService().is_emergency("I have severe chest pain and cannot breathe")
def test_normal_query(): assert not SafetyService().is_emergency("What are healthy hydration habits?")
