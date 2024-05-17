import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import SignIn from "./Pages/SignIn/SignIn";
import SignUp from "./Pages/SignUp/SignUp";
import Patients from "./Pages/Patients/Patients";
import CreatePatient from "./Pages/CreatePatient/CreatePatient";
import AddAppointment from "./Pages/AddAppointment/AddAppointment";
import Patient from "./Pages/Patient/Patient";
import PaymentDone from "./Pages/PaymentDone/PaymentDone";
function App() {

  return (
    <Router>
      <Routes>
        <Route path="/" element={<SignIn/>}/>
        <Route path="/signin" element={<SignIn/>}/>
        <Route path="/signup" element={<SignUp/>}/>
        <Route path="/allpatients" element={<Patients/>}/>
        <Route path="/createpatient" element={<CreatePatient/>}/>
        <Route path="/addappointment/:id" element={<AddAppointment/>}/>
        <Route path="/patient/:id" element={<Patient/>}/>
        <Route path="/paymentdone/:id" element={<PaymentDone/>}/>
      </Routes>
    </Router>
  );
}

export default App;