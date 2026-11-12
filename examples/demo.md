# Welcome to Dillinger

A clean, distraction-free markdown editor. Type on the left, see the rendered output on the right.

---

## Text Formatting

Markdown makes it easy to format text. You can write in **bold**, *italic*, or ~~strikethrough~~. Combine them for ***bold italic*** text. Use `inline code` for technical terms.

## Lists

Unordered lists use dashes, asterisks, or plus signs:

- Import files from GitHub, Dropbox, or Google Drive

- Export to Markdown, HTML, or PDF

- Drag and drop files directly into the editor

Ordered lists are numbered automatically:

1. Write your markdown

2. Preview the rendered output

3. Export or save to the cloud

Nested lists work too:

- Cloud integrations

- GitHub repositories

- Dropbox folders

- Google Drive files

- OneDrive and Bitbucket

- Local features

- Auto-save to browser storage

- Image paste from clipboard

## Task Lists

- [x] Set up the editor

- [x] Write some markdown

- [ ] Connect a cloud service

- [ ] Export the finished document

## Links and Images

Link to any page with [inline links](https://dillinger.io) or use [reference-style links][dillinger].

Images use a similar syntax:

![Imágenes de Paisajes Hermosos | Descarga imágenes gratuitas ...](https://images.unsplash.com/photo-1696864237931-b3a1f15f62c5?fm=jpg&q=60&w=3000&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8M3x8cGFpc2FqZXMlMjBoZXJtb3Nvc3xlbnwwfHwwfHx8MA%3D%3D)

[dillinger]: https://dillinger.io

## Blockquotes

> The art of writing is the art of discovering what you believe.
> 
> — Gustave Flaubert

Blockquotes can contain other markdown elements:

> **Tip:** Use `Cmd+Shift+Z` to enter zen mode for distraction-free writing.

## Code

Fenced code blocks support syntax highlighting:

```javascript
function greet(name) {

return `Hello, ${name}.`;

}
console.log(greet("world"));
```

```python
def fibonacci(n):

    a, b = 0, 1

for _ in range(n):

    a, b = b, a + b

return a
```

### Languages used in class

```kotlin
fun suma(nums: List<Int>): Int {
    var total = 0
    for (n in nums) total += n
    return total
}
```

```kotlin
@Composable
fun Contador(modifier: Modifier = Modifier) {
    var total by remember { mutableStateOf(0) }
    Column(modifier = modifier.fillMaxSize()) {
        Text(text = "Has premut $total voltes", fontSize = 24.sp)
        Button(onClick = { total++ }) { Text("Prem") }
    }
}
```

```java
public class Hola {
    public static void main(String[] args) {
        int suma = 0;
        for (int i = 1; i <= 10; i++) suma += i;
        System.out.println("Suma: " + suma);
    }
}
```

```bash
#!/usr/bin/env bash
for f in *.md; do
    echo "Processant ${f}"
    pandoc "$f" -o "${f%.md}.html" 2>/dev/null || echo "Error"
done
```

```html
<nav class="menu">
    <a href="#inici">Inici</a>
    <a href="#contacte">Contacte</a>
</nav>
```

```css
.menu a:hover {
    color: #e06c75;
    text-decoration: none;
}
```

```c++
#include <iostream>
using namespace std;

int main() {
    int suma = 0;
    for (int i = 1; i <= 10; i++) suma += i;
    cout << "Suma: " << suma << endl;
    return 0;
}
```

```c#
using System;

class Programa {
    static void Main() {
        double preu = 19.95;
        Console.WriteLine($"Preu: {preu:F2} €");
    }
}
```

```php
<?php
function suma(int $a, int $b): int {
    return $a + $b;
}
echo "Suma: " . suma(2, 3);
```

## Tables

| Shortcut | Action             |
| -------- | ------------------ |
| `⌘ ⇧ Z`  | Toggle zen mode    |
| `Escape` | Exit zen mode      |
| `?`      | Keyboard shortcuts |

Tables support alignment:

| Feature          | Status    | Notes           |
|:---------------- |:---------:| ---------------:|
| Markdown editing | Active    | Monaco-powered  |
| Live preview     | Active    | Scroll-synced   |
| Cloud sync       | Available | 5 providers     |
| PDF export       | Available | Server-rendered |

## Footnotes

Dillinger supports extended markdown syntax including footnotes[^1] and definition lists.

[^1]: Footnotes appear at the bottom of the rendered preview.

## Math

Inline math: $E = mc^2$

Block equations:

$$\sum_{i=1}^{n} i = \frac{n(n+1)}{2}$$

---

*Your documents save automatically. Start writing.*
