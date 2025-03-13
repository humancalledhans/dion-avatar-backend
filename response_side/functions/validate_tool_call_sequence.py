def validate_tool_call_sequence(tool_calls):
    """
    Validates that:
    1. If get_yahoo_finance is called, it's followed by a get_agent_*_response function
    2. All functions are properly paired

    Args:
        tool_calls: List of ChatCompletionMessageToolCall objects

    Returns:
        bool: True if the sequence is valid, False otherwise
    """
    # Check if tool_calls exists and has content
    if not tool_calls:
        return False

    # Get all function names in sequence
    function_names = [call.function.name for call in tool_calls]

    # If no functions or only one function that is get_yahoo_finance, return False
    if len(function_names) <= 1 and 'get_yahoo_finance' in function_names:
        return False

    # Check each function and its following function
    for i in range(len(function_names) - 1):
        current_func = function_names[i]
        next_func = function_names[i + 1]

        # If current function is get_yahoo_finance, next must be get_agent_*_response
        if current_func == 'get_yahoo_finance':
            if not (next_func.startswith('get_agent_') and next_func.endswith('_response')):
                return False

    # Check the last function - it should not be get_yahoo_finance
    if function_names and function_names[-1] == 'get_yahoo_finance':
        return False

    return True

