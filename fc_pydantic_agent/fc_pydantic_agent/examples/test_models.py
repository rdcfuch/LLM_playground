import os
import logging
from models import DynamicModel

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_model_creation():
    """Test different model types and error handling."""
    try:
        # Test GPT-4o-mini model
        logger.info("Testing GPT-4o-mini model creation...")
        gpt_model = DynamicModel("gpt-4o-mini")
        assert gpt_model.get_model() is not None
        logger.info("GPT-4o-mini model created successfully")

        # Test Kimi model
        logger.info("\nTesting Kimi model creation...")
        kimi_model = DynamicModel("kimi")
        assert kimi_model.get_model() is not None
        logger.info("Kimi model created successfully")

        # Test DeepSeek model
        logger.info("\nTesting DeepSeek model creation...")
        deepseek_model = DynamicModel("deepseek")
        assert deepseek_model.get_model() is not None
        logger.info("DeepSeek model created successfully")

        # Test Ollama model
        logger.info("\nTesting Ollama model creation...")
        ollama_model = DynamicModel("ollama")
        assert ollama_model.get_model() is not None
        logger.info("Ollama model created successfully")

    except ValueError as e:
        logger.error(f"Error creating model: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False

    return True

def test_error_handling():
    """Test error handling scenarios."""
    try:
        # Test unsupported model type
        logger.info("\nTesting unsupported model type...")
        try:
            invalid_model = DynamicModel("invalid_model")
        except ValueError as e:
            logger.info(f"Expected error caught: {e}")

        # Test missing API credentials
        # Temporarily remove API key to test error handling
        logger.info("\nTesting missing API credentials...")
        api_key = os.getenv("OPENAI_API_KEY")
        os.environ["OPENAI_API_KEY"] = ""
        
        try:
            model = DynamicModel("gpt-4o-mini")
        except ValueError as e:
            logger.info(f"Expected error caught: {e}")
        finally:
            # Restore API key
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key

    except Exception as e:
        logger.error(f"Unexpected error in error handling tests: {e}")
        return False

    return True

if __name__ == "__main__":
    logger.info("Starting DynamicModel tests...\n")
    
    # Run model creation tests
    if test_model_creation():
        logger.info("\nModel creation tests completed successfully")
    else:
        logger.error("\nModel creation tests failed")

    # Run error handling tests
    if test_error_handling():
        logger.info("\nError handling tests completed successfully")
    else:
        logger.error("\nError handling tests failed")