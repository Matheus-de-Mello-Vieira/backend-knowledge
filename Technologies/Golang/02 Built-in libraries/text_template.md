# text/template

For more complex usecases, `fmt.Sprintf` become unfeasible:

``` go
fmt.Sprintf(
	`Generate a JSON list following this example schema: %s 
	for the following instruction: Considering the online purchase transaction with ID %s made by user %s on %s at %s, compile a list of potential fraud indicators ONLY related to the payment method %s, including suspicious behavior, validation failures, or risk signals.
	
	IMPORTANT:
	- List ONLY indicators related to the payment method %s
	- In the "payment_method" field of each item, use EXACTLY the name "%s"
	- DO NOT include indicators related to other payment methods (%s)
	Return ONLY valid JSON using double quotes (") and no additional text, explanations, or comments.`,
	examplePattern,
	transactionID,
	userID,
	transactionDate,
	transactionTime,
	paymentMethod,
	paymentMethod,
	paymentMethod,
	otherPaymentMethod,
)
```

Notice that:

- The **string is long, nested, and instruction-heavy**
- Many **repeated placeholders** must stay perfectly aligned
- Small changes (renaming a field, reordering rules) become error-prone
- Hard to read, test, or reuse without mentally parsing the entire template

For this cases, we can use `text/template`:

```go
package prompts

import (
	"bytes"
	"fmt"
	"text/template"
)

const basePrompt = `Generate a JSON list following this example schema: {{.ExamplePattern}}
for the following instruction: Considering the online purchase transaction with ID {{.TransactionID}} made by user {{.UserID}} on {{.TransactionDate}} at {{.TransactionTime}}, compile a list of potential fraud indicators ONLY related to the payment method {{.PaymentMethod}}, including suspicious behavior, validation failures, or risk signals.

IMPORTANT:
- List ONLY indicators related to the payment method {{.PaymentMethod}}
- In the "payment_method" field of each item, use EXACTLY the name "{{.PaymentMethod}}"
- DO NOT include indicators related to other payment methods ({{.OtherPaymentMethod}})
Return ONLY valid JSON using double quotes (") and no additional text, explanations, or comments.
`

type PromptData struct {
	ExamplePattern     string
	TransactionID      string
	UserID             string
	TransactionDate    string
	TransactionTime    string
	PaymentMethod      string
	OtherPaymentMethod string
}

var basePromptTmpl = template.Must(template.New("basePrompt").Parse(basePrompt))

func BuildPrompt(data PromptData) (string, error) {
	var buf bytes.Buffer
	if err := basePromptTmpl.Execute(&buf, data); err != nil {
		return "", fmt.Errorf("execute basePrompt template: %w", err)
	}
	return buf.String(), nil
}
```

Notice that:

- The prompt is **structurally organized and readable**, with domain intent expressed through named fields (`{{.PaymentMethod}}`, `{{.TransactionID}}`) instead of positional arguments, making the instruction easier to reason about.
- **Semantic placeholders are self-describing**, eliminating fragile positional coupling and ensuring values stay aligned with their meaning rather than their index.
- **Incremental changes are localized and safer**: renaming a field, adding a rule, or reordering instructions typically affects a single template variable or line, not a chain of `fmt.Sprintf` arguments.
- The prompt becomes **straightforward to test, diff, and reuse**, since the base prompt is a constant, execution is deterministic, and variations are driven by structured data instead of manual string assembly.

## Actions

### `if` / `else` — Conditional rendering

Use `if` blocks to include or exclude parts of the prompt based on data presence or boolean flags.

#### Template

```
{{if .IsHighRisk}}
This transaction has been flagged as HIGH RISK and requires additional scrutiny.
{{else}}
This transaction does not currently meet high-risk thresholds.
{{end}
```

#### Data

```
IsHighRisk: true
```

#### Result

```text
This transaction has been flagged as HIGH RISK and requires additional scrutiny.
```

**Key point:**
Zero values (`false`, `0`, `""`, `nil`, empty slices/maps) evaluate as `false`.

### `range` — Iteration (lists, slices, maps)

Used to render repeated sections, such as fraud signals, validation rules, or constraints.

#### Template

```
Identified fraud indicators:
{{range .Indicators}}
- {{.}}
{{end}}
```

#### Data

```go
Indicators: []string{
	"Unusual IP location",
	"Multiple failed CVV attempts",
	"Velocity anomaly",
}
```

#### Result

```text
Identified fraud indicators:
- Unusual IP location
- Multiple failed CVV attempts
- Velocity anomaly
```

#### With `else` (empty collection handling)

```
{{range .Indicators}}
- {{.}}
{{else}}
No fraud indicators were detected.
{{end}}
```

### Nested data access

Templates naturally support structured data, which keeps prompts aligned with domain models.

#### Data

```go
Transaction struct {
	ID     string
	Amount float64
	User   struct {
		ID    string
		Email string
	}
}
```

#### Template

```gotemplate
Transaction {{.Transaction.ID}} was initiated by user {{.Transaction.User.Email}}
for a total amount of {{.Transaction.Amount}}.
```

### `with` — Context narrowing

`with` temporarily changes `.` to a nested object, reducing repetition and improving readability.

#### Template

```gotemplate
{{with .Transaction}}
Transaction {{.ID}} occurred for {{.Amount}} USD.
{{end}}
```

Without `with`, you’d repeat `.Transaction` everywhere.

### Logical operators (`and`, `or`, `not`)

Used inside `if` statements for expressive conditions.

#### Template

```gotemplate
{{if and .IsHighRisk .RequiresManualReview}}
Manual review is mandatory for this transaction.
{{end}}
```

#### Another example

```gotemplate
{{if or .IsChargeback .IsRefund}}
This transaction belongs to a post-payment risk flow.
{{end}}
```

### Comparison operators (`eq`, `ne`, `lt`, `gt`, etc.)

Useful when behavior depends on specific values.

#### Template

```gotemplate
{{if eq .PaymentMethod "credit_card"}}
Apply card-specific fraud heuristics.
{{end}}
```

#### Numeric comparison

```gotemplate
{{if gt .TransactionAmount 1000}}
High-value transaction detected.
{{end}}
```

### Template functions (built-in and custom)

#### Built-in examples

```gotemplate
User ID: {{printf "%q" .UserID}}
Uppercase method: {{upper .PaymentMethod}}   // requires custom func
```

#### Registering custom functions

```go
tmpl := template.New("prompt").Funcs(template.FuncMap{
	"upper": strings.ToUpper,
})
```

This enables **domain-specific formatting logic** without polluting the template with Go code.

### Template composition (`define` / `template`)

Split large prompts into reusable components.

#### Base template

```gotemplate
{{define "risk_section"}}
Risk Level: {{.RiskLevel}}
{{end}}
```

#### Usage

```gotemplate
{{template "risk_section" .}}
```

This is especially valuable for:

- Shared disclaimers
- Repeated rule blocks
- Versioned prompt sections