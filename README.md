# lambda-video-frame-pro-send

### Resumo dos Comandos

```sh
find tests -name 'requirements.txt' -exec pip install -r {} +
pip install coverage coverage-badge
coverage run -m unittest discover -s tests -p '*_test.py'
coverage report -m
coverage html  
```

---