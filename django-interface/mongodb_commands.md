# Comandos MongoDB - DLI Chat

## 🔌 Conectar ao MongoDB

```bash
docker exec -it meu-mongodb mongosh -u admin -p admin --authenticationDatabase admin
```

## 📊 Comandos Básicos

### Ver todos os bancos de dados
```javascript
show dbs
```

### Selecionar o banco de dados do projeto
```javascript
use chat_database
```

### Ver todas as coleções
```javascript
show collections
```

## 📁 Comandos para Coleção `chats`

### Ver todos os chats
```javascript
db.chats.find()
```

### Ver todos os chats formatados (mais legível)
```javascript
db.chats.find().pretty()
```

### Contar quantos chats existem
```javascript
db.chats.countDocuments()
```

### Ver apenas os últimos 5 chats
```javascript
db.chats.find().sort({atualizado_em: -1}).limit(5)
```

### Ver um chat específico por ID
```javascript
// Substitua o ID pelo ID do seu chat
db.chats.findOne({_id: ObjectId("68f8b9b9aea27d3f9d3caf9b")})
```

### Ver apenas título e quantidade de mensagens
```javascript
db.chats.find({}, {
  titulo: 1, 
  criado_em: 1,
  "mensagens": {$size: "$mensagens"}
})
```

### Buscar chats por palavra-chave no título
```javascript
db.chats.find({titulo: {$regex: "teste", $options: "i"}})
```

### Buscar chats que contenham uma pergunta específica
```javascript
db.chats.find({"mensagens.pergunta": {$regex: "Brasil", $options: "i"}})
```

## 🗑️ Comandos de Limpeza

### Deletar um chat específico
```javascript
db.chats.deleteOne({_id: ObjectId("SEU_ID_AQUI")})
```

### Deletar todos os chats (CUIDADO!)
```javascript
db.chats.deleteMany({})
```

### Dropar a coleção inteira (CUIDADO!)
```javascript
db.chats.drop()
```

## 📈 Comandos de Análise

### Ver estatísticas da coleção
```javascript
db.chats.stats()
```

### Ver o tamanho total de dados
```javascript
db.chats.totalSize()
```

### Agregação: Ver quantas mensagens cada chat tem
```javascript
db.chats.aggregate([
  {
    $project: {
      titulo: 1,
      total_mensagens: {$size: "$mensagens"},
      atualizado_em: 1
    }
  },
  {
    $sort: {atualizado_em: -1}
  }
])
```

### Ver total de mensagens em todos os chats
```javascript
db.chats.aggregate([
  {
    $project: {
      total_mensagens: {$size: "$mensagens"}
    }
  },
  {
    $group: {
      _id: null,
      total: {$sum: "$total_mensagens"}
    }
  }
])
```

## 🔍 Comandos de Debug

### Ver estrutura de um documento
```javascript
db.chats.findOne()
```

### Ver apenas os campos disponíveis
```javascript
Object.keys(db.chats.findOne())
```

### Ver a primeira mensagem de cada chat
```javascript
db.chats.find({}, {
  titulo: 1,
  "mensagens": {$slice: 1}
})
```

## 🚪 Sair do MongoDB
```javascript
exit
```
ou pressione `Ctrl+C`

---

## 💡 Dicas

- Use `.pretty()` para formatar a saída
- Use `.limit(N)` para limitar resultados
- Use `.sort({campo: -1})` para ordenar (1 = crescente, -1 = decrescente)
- Use `$regex` para buscar por texto
- Use `$size` para contar elementos em arrays

