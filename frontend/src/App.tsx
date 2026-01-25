import './App.css'

function submitData(submitEvent) {
  submitEvent.preventDefault()
  const data = new FormData(submitEvent.target)
  const values = Object.fromEntries(data.entries())
  console.log(values);
  alert(`You searched for '${values.name}, ${values.age}, ${values.income}'`);
}

function MyForm() {
  return (
    <form onSubmit={submitData}>
      <label>Name:</label><br />
      <input name='name' type='text'/><br />
      <label>Age:</label><br />
      <input name='age' type='number'/><br />
      <label>Income:</label><br />
      <input name='income' type='number'/><br />
      <label>Expenses:</label><br />
      <input name='expenses' type='number'/><br />

      <button type='submit'>Simulate</button>
    </form>
  )
}

function App() {
  return (
    <>
      <MyForm />
   </>
  )
}

export default App
