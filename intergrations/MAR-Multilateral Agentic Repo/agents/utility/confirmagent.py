
class ConfirmAgent:
    """Agent based on Confirm from ..\Nyxion\env\Lib\site-packages\pip\_vendor\rich\prompt.py"""
    
    def __init__(self):
        self.name = "ConfirmAgent"
        self.category = "utility"
        self.status = "active"
    
    def process(self, data):
        """Process data using the original pattern logic"""
            """A yes / no confirmation prompt.
    Example:
        >>> if Confirm.ask("Continue"):
                run_job()
    """
    response_type = bool
    validate_error_message = '[prompt.invalid]Please enter Y or N'
    choices: List[str] = ['y', 'n']
    def render_default(self, default: DefaultType) -> Text:
        """Render the default as (y) or (n) rather than True/False."""
        yes, no = self.choices
        return Text(f'({yes})' if default else f'({no})', style='prompt.default')
    def process_response(self, value: str) -> bool:
        """Convert choices to a bool."""
        value = value.strip().lower()
        if value not in self.choices:
            raise InvalidResponse(self.validate_error_message)
        return value == self.choices[0]
        
    def run(self, *args, **kwargs):
        """Main execution method"""
        return self.process(*args, **kwargs)
