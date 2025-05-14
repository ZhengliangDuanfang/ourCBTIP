def apply_template(template, drug1, drug2):
    template_tokens = template.split()
    # 替换模板中的占位符
    for i, token in enumerate(template_tokens):
        if token.startswith("[Drug"):
            if token == "[Drug1]":
               template_tokens[i] = drug1
            else:
               template_tokens[i] = drug2

    # 连接成句子
    sentence = " ".join(template_tokens)
    return sentence
