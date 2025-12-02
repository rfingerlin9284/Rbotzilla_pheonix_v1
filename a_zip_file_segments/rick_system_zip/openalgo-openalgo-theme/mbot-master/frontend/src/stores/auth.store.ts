/* eslint-disable @typescript-eslint/no-inferrable-types */

import { writable, type Writable } from "svelte/store";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut,
	type Auth, type User, type UserCredential, } from "firebase/auth";
import { initializeApp, getApp, getApps,
	type FirebaseOptions, type FirebaseApp
} from "firebase/app";

const firebaseConfig: FirebaseOptions = {
	apiKey: "AIzaSyABNk9oM5G2gZZy0_XrKAT-eAPI7q6feLs",
	authDomain: "mbotfbase.firebaseapp.com",
	projectId: "mbotfbase",
	storageBucket: "mbotfbase.appspot.com",
	messagingSenderId: "311121570177",
	appId: "1:311121570177:web:e6472526cb1d1eedaba080",
	measurementId: "G-5GXRMHKLR5"
};

const firebaseApp: FirebaseApp = (getApps().length === 0) ?
	initializeApp(firebaseConfig) : getApp();

const auth: Auth = getAuth(firebaseApp);

export const authentication: Writable<{
	user_active: boolean,
	firebase_controlled: boolean,
	id_token: string | null,
	unique_user_id: string | null,
	user: User | null}> = writable(
		{
			user_active: false,
			firebase_controlled: false,
			id_token: null,
			unique_user_id: null,
			user: null
		}
	);

auth.onAuthStateChanged(async (user: User | null) => {
	console.log("Auth state changed.");

	//let user_active: boolean;
	//let firebase_controlled: boolean;
	//let unique_user_id: string | null;
	//let user_id_token: string | null;

	if (user) {
		//user_active = true;
		//firebase_controlled = true;
		//unique_user_id = user.uid;
		//user_id_token = await user.getIdToken();

		const idToken: string = await user.getIdToken();
		authentication.set({
			user_active: true,
			firebase_controlled: true,
			id_token: idToken,
			unique_user_id: user.uid,
			user: user
		});
		console.log("User is logged in.");
		console.log(user);
	} else {
		//user_active = false;
		//firebase_controlled = true;
		//unique_user_id = null;
		//user_id_token = null;

		authentication.set({
			user_active: false,
			firebase_controlled: true,
			id_token: null,
			unique_user_id: null,
			user: null
		});
		console.log("User is not logged in.");
	}

});

export async function login() {
	try {
		const provider: GoogleAuthProvider = new GoogleAuthProvider();
		const result: UserCredential = await signInWithPopup(auth, provider);
		const webAuthToken: string = await result.user.getIdToken();
		authentication.set({
			user_active: true,
			firebase_controlled: true,
			id_token: webAuthToken,
			unique_user_id: result.user.uid,
			user: result.user
		});
	} catch (error) {
		console.error("Error logging in.", error);
	}
}

export async function logout() {
	try {
		await signOut(auth);
		authentication.set({
			user_active: false,
			firebase_controlled: true,
			id_token: null,
			unique_user_id: null,
			user: null
		});
	} catch (error) {
		console.error("Error logging out.", error);
	}
}
