import { useState } from "react";

const API_BASE = "/api";

export default function Auth({ onLogin }) {
  const [isRegistering, setIsRegistering] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    const endpoint = isRegistering ? "/auth/register" : "/auth/login";

    const body = { email, password };
    if (isRegistering) body.name = name;

    try {
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });

      const data = await res.json();

      if (!res.ok) {
        throw new Error(data.error || "Une erreur est survenue");
      }

      if (isRegistering) {
        setIsRegistering(false);
        setError("Compte créé ! Connectez-vous.");
        setPassword("");
      } else {
        onLogin(data.access_token, data.user);
      }
    } catch (err) {
      console.error(err);
      setError(err.message);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-100 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <div className="w-full max-w-sm bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-2xl p-8 shadow-lg">
        <h1 className="text-2xl font-bold mb-2 text-center text-emerald-600 dark:text-emerald-400">
          {isRegistering ? "Créer un compte" : "Connexion"}
        </h1>
        <p className="text-xs text-slate-500 text-center mb-6">
          3Comptes - Gestion de dépenses
        </p>

        {error && (
          <div className={`mb-4 p-2 text-xs rounded border ${error.includes("créé") ? "bg-green-100 text-green-700" : "bg-red-100 text-red-700"}`}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          {isRegistering && (
            <div>
              <label className="block text-xs font-medium mb-1">Nom</label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="w-full rounded-lg border border-slate-300 bg-slate-50 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-emerald-500 dark:bg-slate-950 dark:border-slate-700"
              />
            </div>
          )}

          <div>
            <label className="block text-xs font-medium mb-1">Email</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-slate-50 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-emerald-500 dark:bg-slate-950 dark:border-slate-700"
            />
          </div>

          <div>
            <label className="block text-xs font-medium mb-1">Mot de passe</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full rounded-lg border border-slate-300 bg-slate-50 px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-emerald-500 dark:bg-slate-950 dark:border-slate-700"
            />
          </div>

          <button
            type="submit"
            className="w-full py-2.5 px-4 bg-emerald-500 hover:bg-emerald-600 text-white font-semibold rounded-lg transition"
          >
            {isRegistering ? "S'inscrire" : "Se connecter"}
          </button>
        </form>

        <div className="mt-6 text-center border-t border-slate-100 dark:border-slate-800 pt-4">
          <button
            onClick={() => {
              setIsRegistering(!isRegistering);
              setError("");
            }}
            className="text-xs text-slate-500 hover:text-emerald-500 underline transition"
          >
            {isRegistering
              ? "J'ai déjà un compte ? Se connecter"
              : "Pas encore de compte ? S'inscrire"}
          </button>
        </div>
      </div>
    </div>
  );
}
