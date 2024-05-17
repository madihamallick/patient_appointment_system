import React, { useState } from "react";
import { IoLogOutOutline } from "react-icons/io5";
import { useNavigate } from "react-router-dom";

const CreatePatient = () => {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    name: "",
    email: "",
    mobile: "",
    username: "",
    problem: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();

    const payload = {
      name: formData.name,
      email: formData.email,
      password: formData.password,
      mobile: formData.mobile,
      username: formData.username,
      user_id: localStorage.getItem("user_id"),
    };

    try {
      const response = await fetch(`${process.env.REACT_APP_FAST_API}/patients/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error("Failed to register user");
      }

      navigate("/allpatients");
    } catch (error) {
      console.error(error.message);
    }
  };
  return (
    <div>
      <div
        className="flex justify-end px-5 pt-2 cursor-pointer"
        onClick={() => {
          localStorage.removeItem("user");
          localStorage.removeItem("user_id");
          navigate("/signin");
        }}
      >
        <span className="pt-1 pr-3">{localStorage.getItem("user")}</span>
        <IoLogOutOutline className="text-3xl " />
      </div>
      <h1 class="text-2xl xl:text-3xl font-extrabold text-center  md:pt-28 pt-10">
        Create Patient
      </h1>

      <div class="w-full flex-1 mt-8">
        <div class="mx-auto max-w-md">
          <form onSubmit={handleSubmit}>
            <input
              class="w-full px-8 py-4 my-3 rounded-lg font-medium bg-gray-100 border border-gray-200 placeholder-gray-500 text-sm focus:outline-none focus:border-gray-400 focus:bg-white"
              type="name"
              placeholder="Name"
              value={formData.name}
              onChange={(e) =>
                setFormData({ ...formData, name: e.target.value })
              }
            />
            <input
              class="w-full px-8 py-4 my-3 rounded-lg font-medium bg-gray-100 border border-gray-200 placeholder-gray-500 text-sm focus:outline-none focus:border-gray-400 focus:bg-white"
              type="username"
              placeholder="Username"
              value={formData.username}
              onChange={(e) =>
                setFormData({ ...formData, username: e.target.value })
              }
            />
            <input
              class="w-full px-8 py-4 my-3 rounded-lg font-medium bg-gray-100 border border-gray-200 placeholder-gray-500 text-sm focus:outline-none focus:border-gray-400 focus:bg-white"
              type="email"
              placeholder="Email"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
            />
            <input
              class="w-full px-8 py-4 my-3 rounded-lg font-medium bg-gray-100 border border-gray-200 placeholder-gray-500 text-sm focus:outline-none focus:border-gray-400 focus:bg-white"
              type="phone"
              placeholder="Mobile Number"
              value={formData.mobile}
              onChange={(e) =>
                setFormData({ ...formData, mobile: e.target.value })
              }
            />
            <input
              class="w-full px-8 py-4 my-3 rounded-lg font-medium bg-gray-100 border border-gray-200 placeholder-gray-500 text-sm focus:outline-none focus:border-gray-400 focus:bg-white mt-5"
              type="text"
              placeholder="problem"
              value={formData.problem}
              onChange={(e) =>
                setFormData({ ...formData, problem: e.target.value })
              }
            />
            <button
              type="submit"
              class="mt-5 tracking-wide font-semibold bg-blue-500 text-gray-100 w-full py-4 rounded-lg hover:bg-blue-700 transition-all duration-300 ease-in-out flex items-center justify-center focus:shadow-outline focus:outline-none"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke-width="1.5"
                stroke="currentColor"
                class="w-6 h-6"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  d="M17.25 8.25 21 12m0 0-3.75 3.75M21 12H3"
                />
              </svg>

              <span class="ml-3">Create Patient</span>
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default CreatePatient;
