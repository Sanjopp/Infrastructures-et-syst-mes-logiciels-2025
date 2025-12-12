import { useEffect, useState } from "react";

const API_BASE = "http://127.0.0.1:5001/api";

function App() {
  const [theme, setTheme] = useState("dark");

  useEffect(() => {
    const saved = localStorage.getItem("theme");
    if (saved === "light" || saved === "dark") {
      setTheme(saved);
    }
  }, []);

  useEffect(() => {
    if (theme === "dark") {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  const [tricounts, setTricounts] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [selectedTricount, setSelectedTricount] = useState(null);

  const [loadingList, setLoadingList] = useState(false);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState("");

  const [newName, setNewName] = useState("");

  const [userName, setUserName] = useState("");
  const [userEmail, setUserEmail] = useState("");

  const [desc, setDesc] = useState("");
  const [amount, setAmount] = useState("");
  const [payerId, setPayerId] = useState("");
  const [participants, setParticipants] = useState([]);

  useEffect(() => {
    loadTricounts();
  }, []);

  async function loadTricounts() {
    try {
      setLoadingList(true);
      setError("");
      const res = await fetch(`${API_BASE}/tricounts`);
      if (!res.ok) {
        throw new Error("Failed to load tricounts");
      }
      const data = await res.json();
      setTricounts(data);
    } catch (e) {
      console.error(e);
      setError("Erreur lors du chargement des tricounts.");
    } finally {
      setLoadingList(false);
    }
  }

  async function loadTricountDetail(id) {
    try {
      setLoadingDetail(true);
      setError("");
      const res = await fetch(`${API_BASE}/tricounts/${id}`);
      if (!res.ok) {
        if (res.status === 404) {
          setSelectedTricount(null);
          setError("Tricount introuvable (404).");
          return;
        }
        throw new Error("Failed to load tricount detail");
      }
      const data = await res.json();
      setSelectedTricount(data);
      setSelectedId(id);

      setUserName("");
      setUserEmail("");
      setDesc("");
      setAmount("");
      setPayerId("");
      setParticipants([]);
    } catch (e) {
      console.error(e);
      setError("Erreur lors du chargement du tricount.");
    } finally {
      setLoadingDetail(false);
    }
  }

  async function handleCreateTricount(e) {
    e.preventDefault();
    if (!newName.trim()) return;

    try {
      setError("");
      const res = await fetch(`${API_BASE}/tricounts`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ name: newName.trim() }),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || "Erreur création tricount.");
      }

      const created = await res.json();
      setNewName("");
      await loadTricounts();
      await loadTricountDetail(created.id);
    } catch (e) {
      console.error(e);
      setError(e.message || "Erreur lors de la création du tricount.");
    }
  }

  async function handleAddUser(e) {
    e.preventDefault();
    if (!selectedTricount) return;
    if (!userName.trim()) return;

    try {
      setError("");
      const res = await fetch(
        `${API_BASE}/tricounts/${selectedTricount.id}/users`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: userName.trim(),
            email: userEmail.trim() || null,
          }),
        }
      );

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || "Erreur ajout utilisateur.");
      }

      await loadTricountDetail(selectedTricount.id);
      await loadTricounts();
    } catch (e) {
      console.error(e);
      setError(e.message || "Erreur réseau lors de l'ajout utilisateur.");
    }
  }

  function toggleParticipant(id) {
    setParticipants((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]
    );
  }

  async function handleAddExpense(e) {
    e.preventDefault();
    if (!selectedTricount) return;

    if (!desc.trim() || !amount || !payerId || participants.length === 0) {
      setError("Merci de remplir tous les champs de la dépense.");
      return;
    }

    try {
      setError("");
      const res = await fetch(
        `${API_BASE}/tricounts/${selectedTricount.id}/expenses`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            description: desc.trim(),
            amount: parseFloat(amount),
            payer_id: payerId,
            participants_ids: participants,
          }),
        }
      );

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        throw new Error(data.error || "Erreur ajout dépense.");
      }

      await loadTricountDetail(selectedTricount.id);
      await loadTricounts();
    } catch (e) {
      console.error(e);
      setError(e.message || "Erreur réseau lors de l'ajout dépense.");
    }
  }

  async function handleDeleteUser(userId) {
    if (!selectedId) return;
    const confirmDelete = window.confirm(
      "Supprimer cet utilisateur ? (impossible s'il est utilisé dans une dépense)"
    );
    if (!confirmDelete) return;

    try {
      setError("");
      const res = await fetch(
        `${API_BASE}/tricounts/${selectedId}/users/${userId}`,
        {
          method: "DELETE",
        }
      );

      const data = await res.json();

      if (!res.ok) {
        setError(
          data.error || "Erreur lors de la suppression de l'utilisateur."
        );
        return;
      }

      setSelectedTricount(data);
      setTricounts((prev) =>
        prev.map((t) =>
          t.id === selectedId
            ? {
                ...t,
                users_count: data.users.length,
                expenses_count: data.expenses.length,
              }
            : t
        )
      );
    } catch (e) {
      console.error(e);
      setError("Erreur réseau lors de la suppression de l'utilisateur.");
    }
  }

  async function handleDeleteExpense(expenseId) {
    if (!selectedId) return;
    const confirmDelete = window.confirm("Supprimer cette dépense ?");
    if (!confirmDelete) return;

    try {
      setError("");
      const res = await fetch(
        `${API_BASE}/tricounts/${selectedId}/expenses/${expenseId}`,
        {
          method: "DELETE",
        }
      );

      const data = await res.json();

      if (!res.ok) {
        setError(data.error || "Erreur lors de la suppression de la dépense.");
        return;
      }

      setSelectedTricount(data);
      setTricounts((prev) =>
        prev.map((t) =>
          t.id === selectedId
            ? {
                ...t,
                users_count: data.users.length,
                expenses_count: data.expenses.length,
              }
            : t
        )
      );
    } catch (e) {
      console.error(e);
      setError("Erreur réseau lors de la suppression de la dépense.");
    }
  }

  const balances = selectedTricount?.balances || {};
  const settlements = selectedTricount?.settlements || [];

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900 dark:bg-slate-950 dark:text-slate-100">
      <div className="max-w-6xl mx-auto flex gap-6 px-6 py-8">
        {/* COLONNE GAUCHE : liste + création */}
        <aside className="w-1/3 bg-white border border-slate-200 rounded-2xl p-4 flex flex-col gap-4 dark:bg-slate-900 dark:border-slate-800">
          <header className="flex items-center justify-between">
            <div>
              <h1 className="text-xl font-semibold tracking-tight">
                Tricount React
              </h1>
              <p className="text-xs text-slate-500 dark:text-slate-400">
                Gestion simple des dépenses de groupe
              </p>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={toggleTheme}
                className="inline-flex items-center gap-1 rounded-full border border-slate-300 bg-slate-100 px-2 py-1 text-[11px] text-slate-700 hover:bg-slate-200 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700 transition"
              >
                {theme === "dark" ? "☀️ Clair" : "🌙 Sombre"}
              </button>
              <span className="inline-flex h-8 items-center rounded-full bg-emerald-500/10 px-3 text-xs font-medium text-emerald-700 border border-emerald-500/30 dark:text-emerald-300 dark:border-emerald-500/40">
                Demo
              </span>
            </div>
          </header>

          {loadingList && (
            <p className="text-xs text-slate-500 dark:text-slate-400">
              Chargement des tricounts…
            </p>
          )}

          {error && (
            <div className="text-xs rounded-lg border border-red-500/50 bg-red-500/10 text-red-800 px-3 py-2 dark:text-red-200">
              {error}
            </div>
          )}

          <div className="flex-1 flex flex-col gap-2 overflow-hidden">
            <h2 className="text-sm font-semibold text-slate-800 dark:text-slate-200">
              Mes tricounts
            </h2>
            <div className="flex-1 overflow-y-auto pr-1">
              {tricounts.length === 0 ? (
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Aucun tricount pour le moment.
                </p>
              ) : (
                <ul className="space-y-1 text-sm">
                  {tricounts.map((t) => (
                    <li key={t.id}>
                      <button
                        onClick={() => loadTricountDetail(t.id)}
                        className={`w-full text-left px-3 py-2 rounded-xl border text-xs transition
                          ${
                            t.id === selectedId
                              ? "border-emerald-500/70 bg-emerald-500/10 text-emerald-900 dark:text-emerald-100"
                              : "border-transparent bg-slate-100 hover:bg-slate-50 hover:border-slate-200 dark:bg-slate-800/60 dark:hover:bg-slate-800 dark:hover:border-slate-700"
                          }`}
                      >
                        <div className="flex items-center justify-between">
                          <span className="font-semibold text-sm">
                            {t.name}
                          </span>
                          <span className="text-[10px] uppercase text-slate-400">
                            {t.currency}
                          </span>
                        </div>
                        <div className="mt-1 flex items-center gap-2 text-[11px] text-slate-500 dark:text-slate-400">
                          <span>{t.users_count} utilisateurs</span>
                          <span>•</span>
                          <span>{t.expenses_count} dépenses</span>
                        </div>
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </div>
          </div>

          <div className="border-t border-slate-200 pt-3 dark:border-slate-800">
            <h3 className="text-xs font-semibold text-slate-700 dark:text-slate-300 mb-2">
              Nouveau tricount
            </h3>
            <form onSubmit={handleCreateTricount} className="space-y-2">
              <input
                type="text"
                placeholder="Ex : Voyage Espagne"
                value={newName}
                onChange={(e) => setNewName(e.target.value)}
                className="w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 dark:border-slate-700 dark:bg-slate-900 dark:placeholder:text-slate-500"
              />
              <button
                type="submit"
                className="w-full inline-flex items-center justify-center rounded-lg bg-emerald-500 px-3 py-1.5 text-xs font-medium text-slate-950 hover:bg-emerald-400 transition"
              >
                Créer le tricount
              </button>
            </form>
          </div>
        </aside>

        {/* COLONNE DROITE : détail */}
        <main className="flex-1 flex flex-col gap-4">
          {!selectedTricount && !loadingDetail && (
            <div className="h-full flex items-center justify-center text-slate-500 text-sm">
              Sélectionne un tricount à gauche pour voir le détail.
            </div>
          )}

          {loadingDetail && (
            <div className="h-full flex items-center justify-center text-slate-400 text-sm">
              Chargement du tricount…
            </div>
          )}

          {selectedTricount && (
            <>
              {/* Header tricount */}
              <section className="bg-white border border-slate-200 rounded-2xl p-4 flex items-center justify-between dark:bg-slate-900 dark:border-slate-800">
                <div>
                  <h2 className="text-lg font-semibold">
                    {selectedTricount.name}
                  </h2>
                  <p className="text-xs text-slate-500 dark:text-slate-400">
                    Devise :{" "}
                    <span className="font-mono">
                      {selectedTricount.currency}
                    </span>
                  </p>
                </div>
              </section>

              <div className="grid grid-cols-2 gap-4">
                {/* UTILISATEURS */}
                <section className="bg-white border border-slate-200 rounded-2xl p-4 flex flex-col gap-3 dark:bg-slate-900 dark:border-slate-800">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                      Utilisateurs
                    </h3>
                    <span className="text-[11px] text-slate-500 dark:text-slate-400">
                      {selectedTricount.users?.length || 0} au total
                    </span>
                  </div>

                  <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
                    {selectedTricount.users?.length === 0 ? (
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        Aucun utilisateur pour l’instant.
                      </p>
                    ) : (
                      selectedTricount.users.map((u) => (
                        <div
                          key={u.id}
                          className="flex items-center justify-between text-xs rounded-lg bg-slate-50 px-3 py-2 dark:bg-slate-800/70"
                        >
                          <div>
                            <div className="font-medium">{u.name}</div>
                            {u.email && (
                              <div className="text-slate-500 dark:text-slate-400">
                                {u.email}
                              </div>
                            )}
                          </div>
                          <button
                            onClick={() => handleDeleteUser(u.id)}
                            className="text-[11px] text-red-500 hover:text-red-600 dark:text-red-300 dark:hover:text-red-200"
                          >
                            Supprimer
                          </button>
                        </div>
                      ))
                    )}
                  </div>

                  <div className="border-t border-slate-200 pt-3 dark:border-slate-800">
                    <h4 className="text-xs font-semibold text-slate-800 dark:text-slate-200 mb-2">
                      Ajouter un utilisateur
                    </h4>
                    <form onSubmit={handleAddUser} className="space-y-2">
                      <input
                        type="text"
                        placeholder="Nom"
                        value={userName}
                        onChange={(e) => setUserName(e.target.value)}
                        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 dark:border-slate-700 dark:bg-slate-950 dark:placeholder:text-slate-500"
                      />
                      <input
                        type="email"
                        placeholder="Email (optionnel)"
                        value={userEmail}
                        onChange={(e) => setUserEmail(e.target.value)}
                        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-xs placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 dark:border-slate-700 dark:bg-slate-950 dark:placeholder:text-slate-500"
                      />
                      <button
                        type="submit"
                        className="inline-flex items-center justify-center rounded-lg bg-slate-900 px-3 py-1.5 text-xs font-medium text-slate-50 hover:bg-black transition dark:bg-slate-100 dark:text-slate-900 dark:hover:bg-white"
                      >
                        Ajouter
                      </button>
                    </form>
                  </div>
                </section>

                {/* DÉPENSES */}
                <section className="bg-white border border-slate-200 rounded-2xl p-4 flex flex-col gap-3 dark:bg-slate-900 dark:border-slate-800">
                  <div className="flex items-center justify-between">
                    <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                      Dépenses
                    </h3>
                    <span className="text-[11px] text-slate-500 dark:text-slate-400">
                      {selectedTricount.expenses?.length || 0} au total
                    </span>
                  </div>

                  <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
                    {selectedTricount.expenses?.length === 0 ? (
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        Aucune dépense pour l’instant.
                      </p>
                    ) : (
                      selectedTricount.expenses.map((e) => {
                        const payer = selectedTricount.users.find(
                          (u) => u.id === e.payer_id
                        );
                        return (
                          <div
                            key={e.id}
                            className="rounded-lg bg-slate-50 px-3 py-2 text-xs flex items-start justify-between gap-2 dark:bg-slate-800/70"
                          >
                            <div>
                              <div className="font-medium">
                                {e.description}
                              </div>
                              <div className="text-slate-800 dark:text-slate-300">
                                {e.amount.toFixed
                                  ? e.amount.toFixed(2)
                                  : Number(e.amount).toFixed(2)}{" "}
                                {e.currency}
                              </div>
                              <div className="text-[11px] text-slate-500 dark:text-slate-400">
                                Payé par{" "}
                                <span className="font-medium">
                                  {payer?.name || "??"}
                                </span>
                              </div>
                            </div>
                            <button
                              onClick={() => handleDeleteExpense(e.id)}
                              className="text-[11px] text-red-500 hover:text-red-600 dark:text-red-300 dark:hover:text-red-200"
                            >
                              Supprimer
                            </button>
                          </div>
                        );
                      })
                    )}
                  </div>

                  <div className="border-t border-slate-200 pt-3 dark:border-slate-800">
                    <h4 className="text-xs font-semibold text-slate-800 dark:text-slate-200 mb-2">
                      Ajouter une dépense
                    </h4>
                    <form
                      onSubmit={handleAddExpense}
                      className="space-y-2 text-xs"
                    >
                      <input
                        type="text"
                        placeholder="Description"
                        value={desc}
                        onChange={(e) => setDesc(e.target.value)}
                        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 dark:border-slate-700 dark:bg-slate-950 dark:placeholder:text-slate-500"
                      />
                      <input
                        type="number"
                        step="0.01"
                        placeholder="Montant"
                        value={amount}
                        onChange={(e) => setAmount(e.target.value)}
                        className="w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 placeholder:text-slate-400 focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 dark:border-slate-700 dark:bg-slate-950 dark:placeholder:text-slate-500"
                      />

                      <div className="flex items-center gap-2">
                        <span className="text-[11px] text-slate-500 dark:text-slate-400">
                          Payeur :
                        </span>
                        <select
                          value={payerId}
                          onChange={(e) => setPayerId(e.target.value)}
                          className="flex-1 rounded-lg border border-slate-300 bg-white px-2 py-1 text-xs focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:border-emerald-500 dark:border-slate-700 dark:bg-slate-950"
                        >
                          <option value="">-- choisir --</option>
                          {selectedTricount.users.map((u) => (
                            <option key={u.id} value={u.id}>
                              {u.name}
                            </option>
                          ))}
                        </select>
                      </div>

                      <div className="space-y-1">
                        <div className="text-[11px] text-slate-500 dark:text-slate-400">
                          Participants :
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {selectedTricount.users.map((u) => (
                            <label
                              key={u.id}
                              className="inline-flex items-center gap-1 rounded-full bg-slate-100 px-2 py-1 text-[11px] cursor-pointer dark:bg-slate-800/80"
                            >
                              <input
                                type="checkbox"
                                className="h-3 w-3 rounded border-slate-400 bg-white dark:border-slate-600 dark:bg-slate-900"
                                checked={participants.includes(u.id)}
                                onChange={() => toggleParticipant(u.id)}
                              />
                              <span>{u.name}</span>
                            </label>
                          ))}
                        </div>
                      </div>

                      <button
                        type="submit"
                        className="inline-flex items-center justify-center rounded-lg bg-emerald-500 px-3 py-1.5 text-xs font-medium text-slate-950 hover:bg-emerald-400 transition"
                      >
                        Ajouter la dépense
                      </button>
                    </form>
                  </div>
                </section>
              </div>

              {/* SOLDES & RÈGLEMENTS */}
              <div className="grid grid-cols-2 gap-4">
                <section className="bg-white border border-slate-200 rounded-2xl p-4 dark:bg-slate-900 dark:border-slate-800">
                  <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-2">
                    Soldes
                  </h3>
                  {selectedTricount.users.length === 0 ? (
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Ajoute des utilisateurs pour voir les soldes.
                    </p>
                  ) : (
                    <ul className="space-y-1 text-xs">
                      {selectedTricount.users.map((u) => {
                        const bal =
                          balances && typeof balances === "object"
                            ? balances[u.id] ?? 0
                            : 0;
                        let statut = "est à l'équilibre";
                        if (bal > 0) statut = "doit recevoir";
                        if (bal < 0) statut = "doit payer";
                        return (
                          <li
                            key={u.id}
                            className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-1.5 dark:bg-slate-800/70"
                          >
                            <span>{u.name}</span>
                            <span>
                              {bal.toFixed(2)} {selectedTricount.currency}{" "}
                              <span className="text-slate-500 dark:text-slate-400">
                                ({statut})
                              </span>
                            </span>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </section>

                <section className="bg-white border border-slate-200 rounded-2xl p-4 dark:bg-slate-900 dark:border-slate-800">
                  <h3 className="text-sm font-semibold text-slate-900 dark:text-slate-100 mb-2">
                    Règlements optimisés
                  </h3>
                  {settlements.length === 0 ? (
                    <p className="text-xs text-slate-500 dark:text-slate-400">
                      Tout est déjà équilibré 👌
                    </p>
                  ) : (
                    <ul className="space-y-1 text-xs">
                      {settlements.map((s, idx) => {
                        const fromUser = selectedTricount.users.find(
                          (u) => u.id === s.from_id || u.id === s.from
                        );
                        const toUser = selectedTricount.users.find(
                          (u) => u.id === s.to_id || u.id === s.to
                        );
                        const amount =
                          s.amount?.toFixed?.(2) ??
                          Number(s.amount || 0).toFixed(2);
                        return (
                          <li
                            key={idx}
                            className="flex items-center justify-between rounded-lg bg-slate-50 px-3 py-1.5 dark:bg-slate-800/70"
                          >
                            <span>
                              {fromUser?.name ?? "??"} →{" "}
                              {toUser?.name ?? "??"}
                            </span>
                            <span>
                              {amount} {selectedTricount.currency}
                            </span>
                          </li>
                        );
                      })}
                    </ul>
                  )}
                </section>
              </div>
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default App;
