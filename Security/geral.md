# Geral

* Nunca confie na entrada do usuário
* considere tudo que vem pela internet como malicioso
* trate todas as excessões 
* Logging: importante para investigar
  * entradas de usuários maliciosos podem envenenar o log, de forma a dificultar as investigações 
* Controle de acesso robusto
  * nunca de informacoes de graça, como "email já cadastrado", "telefone já em uso" ou uma mensagem de erro muito verbosa. 
    * O atacando pode ficar vasculhando a aplicação, juntar muitos pequenos fragmentos de informacoes e assim formentar ataques maiores.
* autorizacao entrada
* Validações e double checks sempre no back-end
  * diferente do frontend, o atacante externo nao consegue alterar.
* Use sempre libraries, frameworks e servidores atualizados
* nunca use segredos ou senhas harded coded
* apply security in layers

## Demonstração de Vulnerabilidade: Geração de Senhas com `Random`

Imagine um sistema real:

> “Esse gerador é usado para criar senhas temporárias enviadas por e-mail quando um usuário solicita reset de senha.”

```java
import java.util.Random;

public class PasswordResetGenerator {
    private static final Random rand = new Random(); // VULNERÁVEL

    public static String generateTempPassword() {
        StringBuilder buf = new StringBuilder();
        for (int i = 0; i < 10; i++) {
            buf.append((char) (rand.nextInt(26) + 'a'));
        }
        return buf.toString();
    }
}
```

Agora, o ponto crítico:

> Um atacante descobre — por engenharia social, documentação vazada ou análise de comportamento — que o sistema usa **java.util.Random** para gerar esses tokens.

A partir disso, a exploração é totalmente possível.

### Passo a passo do ataque

1. O atacante coleta algumas senhas geradas
    Ele pode solicitar resets para contas próprias várias vezes:

    ```java
    String s1 = PasswordResetGenerator.generateTempPassword();
    String s2 = PasswordResetGenerator.generateTempPassword();
    String s3 = PasswordResetGenerator.generateTempPassword();
    ```

    Com apenas algumas amostras, ele obtém múltiplas saídas consecutivas do mesmo gerador.

2. Ele reconstrói o estado interno do `Random`

    O `java.util.Random` é baseado em algoritmo LCG (Linear Congruential Generator), cujo estado tem 48 bits.
     Pesquisadores e ferramentas públicas conseguem recuperar esse estado com poucas saídas consecutivas.

    O atacante usa um código como este (exemplo simplificado):

    ```java
    public class PredictRandom {
        private long state;

        public PredictRandom(long leakedState) {
            this.state = leakedState;
        }

        public int nextInt(int bound) {
            state = (state * 25214903917L + 11) & ((1L << 48) - 1);
            return (int)((state >>> 17) % bound);
        }
    }
    ```

    Ao ajustar o estado inicial, ele consegue **prever exatamente as próximas senhas** que o sistema irá gerar.

3. Ele dispara um reset para a vítima

    O atacante envia:

    ```
    “Esqueci minha senha” → conta da vítima
    ```

    Antes que a vítima abra o e-mail, o servidor gera:

    ```java
    String next = PasswordResetGenerator.generateTempPassword();
    ```

    Mas como o atacante já reconstruiu o estado interno, ele calcula isso localmente:

    ```java
    PredictRandom pr = new PredictRandom(leakedState);
    String predicted = pr.predictNextPassword(); // atacante sabe o token exato
    ```

4. Ele usa a senha temporária antes da vítima

    O invasor faz login imediatamente utilizando **a senha que ele já previu**.

    Depois disso, redefine a senha da conta — comprometendo totalmente o usuário alvo.

### Conclusão 

O ataque funciona porque:

- `Random` é **previsível**,
- seu estado interno pode ser reconstruído,
- e o sistema **reutiliza o mesmo gerador** para tokens de segurança.

Qualquer mecanismo de recuperação de conta baseado em números previsíveis é **totalmente comprometido**.

A correção esperada:

```java
import java.security.SecureRandom;

private static final SecureRandom rand = new SecureRandom();
```