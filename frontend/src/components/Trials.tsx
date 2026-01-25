import React, { useEffect, useState, createContext, useContext } from "react";

interface Trial {
    name: string,
    age: number,
    income: number,
    expenses: number
}

const TrialsContext = createContext({
  trials: [], fetchTrials: () => {}
})

export default function Trials() {
    const [trials, setTrials] = useState([])
    const fetchTrials = async () => {
        const response = await fetch("http://127.0.0.1:8000/simulate")
        const trials = await response.json()
        setTrials(trials.data)
    }
    useEffect(() => {
        fetchTrials()
    }, [])

    return (
        <TrialsContext.Provider value={{trials, fetchTrials}}>
            <div>
                {trials.map((trial: Trial) => (
                    <b key={trial.name}>{trial.name} (todo.age): {trial.income}{trial.expenses}</b>
                ))}
            </div>
        </TrialsContext.Provider>
    )
}