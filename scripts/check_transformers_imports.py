try:
    from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
    print('ok imports')
except Exception as e:
    import traceback
    traceback.print_exc()
